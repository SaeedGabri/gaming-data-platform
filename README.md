# Real-Time Gaming Data & AI Platform

A production-style portfolio project for a Senior Data Engineer role using:

- Google Cloud Platform
- Google Cloud Storage
- BigQuery
- Pub/Sub and Kafka
- Airflow / Cloud Composer
- dbt
- Python and SQL
- Terraform
- GitHub Actions
- Monitoring and data-quality controls
- RAG and AI-agent workflows
- Power BI

## Business scenario

The platform simulates a regulated online gaming company that needs trusted batch and real-time data for:

- player activity
- payments
- game sessions
- revenue reporting
- fraud and anomaly detection
- responsible-gaming monitoring
- operational support
- AI-assisted data and runbook discovery

All data is synthetic.

## First milestone

The first working flow is:

Synthetic CSV files → Python validation → Raw storage → BigQuery Bronze → dbt Silver/Gold → Power BI

Airflow, streaming, Terraform, CI/CD, monitoring, and AI are added after the basic batch pipeline works.

## Run the local data generator on Windows

1. Open PowerShell in the project folder.
2. Run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\setup_local.ps1
.\scripts\run_generator.ps1
```

Generated files will appear under `data/generated`.

## Main source files

- `players_YYYYMMDD.csv`
- `games_YYYYMMDD.csv`
- `payment_transactions_YYYYMMDD.csv`

## Design principles

- idempotent processing
- audit metadata on every record
- incremental loading
- duplicate detection
- late-arriving data handling
- rejected-record quarantine
- source-to-target reconciliation
- testable transformations
- infrastructure as code
- traceable AI answers
