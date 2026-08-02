from __future__ import annotations

import pendulum
from airflow.sdk import dag, task


@dag(
    dag_id="gaming_pipeline_smoke_test",
    description="Validates that the local gaming Airflow environment works.",
    schedule=None,
    start_date=pendulum.datetime(2026, 8, 1, tz="UTC"),
    catchup=False,
    tags=["gaming", "learning"],
)
def gaming_pipeline_smoke_test():

    @task
    def read_batch_counts() -> dict:
        batch_counts = {
            "players": 1000,
            "games": 100,
            "payments": 5500,
        }

        print(f"Received batch counts: {batch_counts}")
        return batch_counts

    @task
    def validate_batch_counts(batch_counts: dict) -> dict:
        if batch_counts["players"] <= 0:
            raise ValueError("No player records found.")

        if batch_counts["games"] <= 0:
            raise ValueError("No game records found.")

        if batch_counts["payments"] <= 0:
            raise ValueError("No payment records found.")

        summary = {
            "status": "VALIDATED",
            "total_rows": sum(batch_counts.values()),
        }

        print(f"Validation result: {summary}")
        return summary

    @task
    def complete_pipeline(summary: dict) -> None:
        print("Gaming pipeline smoke test completed successfully.")
        print(f"Final summary: {summary}")

    batch_counts = read_batch_counts()
    validation_summary = validate_batch_counts(batch_counts)
    complete_pipeline(validation_summary)


gaming_pipeline_smoke_test()