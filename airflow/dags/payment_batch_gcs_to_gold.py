from __future__ import annotations

from datetime import timedelta

import pendulum

from airflow.sdk import DAG, Param
from airflow.providers.google.cloud.sensors.gcs import (
    GCSObjectExistenceSensor,
)
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import (
    GCSToBigQueryOperator,
)
from airflow.providers.google.cloud.operators.bigquery import (
    BigQueryCheckOperator,
    BigQueryDeleteTableOperator,
    BigQueryInsertJobOperator,
)
from airflow.providers.standard.operators.bash import BashOperator


PROJECT_ID = "gaming-data-platform-dev"
LOCATION = "me-central1"
BUCKET = "gaming-data-platform-dev-saeed-raw"

STAGE_TABLE = (
    "gaming-data-platform-dev."
    "gaming_bronze."
    "payment_transactions_runtime_stage"
)

BRONZE_TABLE = (
    "gaming-data-platform-dev."
    "gaming_bronze."
    "payment_transactions"
)

GOLD_TABLE = (
    "gaming-data-platform-dev."
    "gaming_gold."
    "fct_payment_transactions"
)

SCHEMA_FIELDS = [
    {"name": "transaction_id", "type": "STRING", "mode": "REQUIRED"},
    {"name": "player_id", "type": "STRING", "mode": "REQUIRED"},
    {"name": "transaction_type", "type": "STRING", "mode": "REQUIRED"},
    {"name": "amount", "type": "NUMERIC", "mode": "REQUIRED"},
    {"name": "currency", "type": "STRING", "mode": "REQUIRED"},
    {"name": "payment_method", "type": "STRING", "mode": "REQUIRED"},
    {"name": "transaction_status", "type": "STRING", "mode": "REQUIRED"},
    {"name": "event_timestamp", "type": "TIMESTAMP", "mode": "REQUIRED"},
    {
        "name": "ingestion_timestamp",
        "type": "TIMESTAMP",
        "mode": "REQUIRED",
    },
    {"name": "source_system", "type": "STRING", "mode": "REQUIRED"},
    {"name": "batch_id", "type": "STRING", "mode": "REQUIRED"},
]


with DAG(
    dag_id="payment_batch_gcs_to_gold",
    description=(
        "Processes a parameterized payment file from "
        "GCS through Bronze, Silver, and Gold."
    ),
    schedule=None,
    start_date=pendulum.datetime(2026, 8, 1, tz="UTC"),
    catchup=False,
    max_active_runs=1,
    render_template_as_native_obj=True,
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=1),
    },
    params={
        "object_name": Param(
            default=(
                "batch/landing/2026-08-02/"
                "payment_transactions_20260802_batch4.csv"
            ),
            type="string",
            title="GCS object path",
            description=(
                "Path inside the raw GCS bucket. "
                "Do not include gs:// or the bucket name."
            ),
            minLength=5,
        ),
        "batch_id": Param(
            default="BATCH-20260802-200000-04",
            type="string",
            title="Batch ID",
            description=(
                "Batch ID expected inside every row of the source file."
            ),
            minLength=5,
        ),
    },
    tags=["gaming", "gcs", "bigquery", "dbt"],
) as dag:

    wait_for_payment_file = GCSObjectExistenceSensor(
        task_id="wait_for_payment_file",
        bucket=BUCKET,
        object="{{ params.object_name }}",
        google_cloud_conn_id="google_cloud_default",
        poke_interval=10,
        timeout=300,
        deferrable=False,
    )

    load_batch_to_stage = GCSToBigQueryOperator(
        task_id="load_batch_to_stage",
        bucket=BUCKET,
        source_objects=["{{ params.object_name }}"],
        destination_project_dataset_table=STAGE_TABLE,
        schema_fields=SCHEMA_FIELDS,
        source_format="CSV",
        skip_leading_rows=1,
        create_disposition="CREATE_IF_NEEDED",
        write_disposition="WRITE_TRUNCATE",
        autodetect=False,
        project_id=PROJECT_ID,
        location=LOCATION,
        gcp_conn_id="google_cloud_default",
    )

    check_stage_batch = BigQueryCheckOperator(
        task_id="check_stage_batch",
        sql=f"""
            SELECT
                COUNT(*) > 0
                AND COUNTIF(
                    batch_id != '{{{{ params.batch_id }}}}'
                ) = 0
            FROM `{STAGE_TABLE}`
        """,
        use_legacy_sql=False,
        project_id=PROJECT_ID,
        location=LOCATION,
        gcp_conn_id="google_cloud_default",
    )

    merge_batch_into_bronze = BigQueryInsertJobOperator(
        task_id="merge_batch_into_bronze",
        project_id=PROJECT_ID,
        location=LOCATION,
        gcp_conn_id="google_cloud_default",
        configuration={
            "query": {
                "query": f"""
                    MERGE `{BRONZE_TABLE}` AS target
                    USING `{STAGE_TABLE}` AS source
                    ON target.transaction_id = source.transaction_id

                    WHEN MATCHED THEN
                      UPDATE SET
                        player_id = source.player_id,
                        transaction_type = source.transaction_type,
                        amount = source.amount,
                        currency = source.currency,
                        payment_method = source.payment_method,
                        transaction_status =
                            source.transaction_status,
                        event_timestamp =
                            source.event_timestamp,
                        ingestion_timestamp =
                            source.ingestion_timestamp,
                        source_system = source.source_system,
                        batch_id = source.batch_id

                    WHEN NOT MATCHED THEN
                      INSERT (
                        transaction_id,
                        player_id,
                        transaction_type,
                        amount,
                        currency,
                        payment_method,
                        transaction_status,
                        event_timestamp,
                        ingestion_timestamp,
                        source_system,
                        batch_id
                      )
                      VALUES (
                        source.transaction_id,
                        source.player_id,
                        source.transaction_type,
                        source.amount,
                        source.currency,
                        source.payment_method,
                        source.transaction_status,
                        source.event_timestamp,
                        source.ingestion_timestamp,
                        source.source_system,
                        source.batch_id
                      )
                """,
                "useLegacySql": False,
            }
        },
    )

    run_dbt_pipeline = BashOperator(
        task_id="run_dbt_pipeline",
        bash_command=(
            "rm -rf /tmp/dbt-target /tmp/dbt-logs && "
            "dbt build "
            "--no-partial-parse "
            "--select +fct_payment_transactions "
            "--project-dir /opt/airflow/dbt "
            "--profiles-dir /home/airflow/.dbt "
            "--target-path /tmp/dbt-target "
            "--log-path /tmp/dbt-logs"
        ),
    )

    check_bronze_batch = BigQueryCheckOperator(
        task_id="check_bronze_batch",
        sql=f"""
            SELECT
                (
                    SELECT COUNT(*)
                    FROM `{BRONZE_TABLE}`
                    WHERE batch_id = '{{{{ params.batch_id }}}}'
                )
                =
                (
                    SELECT COUNT(*)
                    FROM `{STAGE_TABLE}`
                    WHERE batch_id = '{{{{ params.batch_id }}}}'
                )
                AND
                (
                    SELECT COUNT(*)
                    FROM `{STAGE_TABLE}`
                    WHERE batch_id = '{{{{ params.batch_id }}}}'
                ) > 0
        """,
        use_legacy_sql=False,
        project_id=PROJECT_ID,
        location=LOCATION,
        gcp_conn_id="google_cloud_default",
    )

    check_gold_batch = BigQueryCheckOperator(
        task_id="check_gold_batch",
        sql=f"""
            SELECT
                (
                    SELECT COUNT(*)
                    FROM `{GOLD_TABLE}`
                    WHERE batch_id = '{{{{ params.batch_id }}}}'
                )
                =
                (
                    SELECT COUNT(*)
                    FROM `{STAGE_TABLE}`
                    WHERE batch_id = '{{{{ params.batch_id }}}}'
                )
                AND
                (
                    SELECT COUNT(*)
                    FROM `{STAGE_TABLE}`
                    WHERE batch_id = '{{{{ params.batch_id }}}}'
                ) > 0
        """,
        use_legacy_sql=False,
        project_id=PROJECT_ID,
        location=LOCATION,
        gcp_conn_id="google_cloud_default",
    )

    delete_stage_table = BigQueryDeleteTableOperator(
        task_id="delete_stage_table",
        deletion_dataset_table=STAGE_TABLE,
        ignore_if_missing=True,
        location=LOCATION,
        gcp_conn_id="google_cloud_default",
    )

    (
        wait_for_payment_file
        >> load_batch_to_stage
        >> check_stage_batch
        >> merge_batch_into_bronze
        >> run_dbt_pipeline
    )

    run_dbt_pipeline >> check_bronze_batch
    run_dbt_pipeline >> check_gold_batch

    [check_bronze_batch, check_gold_batch] >> delete_stage_table