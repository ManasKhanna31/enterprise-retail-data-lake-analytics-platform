# Interview preparation

The platform ingests retail data from files and API-shaped sources, preserves raw snapshots, applies quality gates, and produces a sales fact suitable for a dimensional warehouse. Kafka and Airflow modules are included for integration deployment; AWS and Power BI remain documented extensions.

Key answers: fact grain is one order item; Bronze is replayable raw input; Silver is validated and deduplicated; Gold is business-ready; MinIO provides an S3-compatible local contract; Redis is intended for hot analytics reads; and no production CDC or cloud deployment is claimed.
