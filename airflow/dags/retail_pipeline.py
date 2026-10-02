"""Airflow DAG for the retail data pipeline."""

import sys
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator


PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def run_extract():
    from scripts.extract_sources import main
    main()


def run_quality_gate():
    from scripts.quality_gate import main
    main()


def run_warehouse():
    from scripts.load_warehouse import main
    main()


with DAG(
    "retail_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
    },
) as dag:

    extract = PythonOperator(
        task_id="extract_sources",
        python_callable=run_extract,
    )

    quality = PythonOperator(
        task_id="data_quality_gate",
        python_callable=run_quality_gate,
    )

    warehouse = PythonOperator(
        task_id="load_warehouse",
        python_callable=run_warehouse,
    )

    extract >> quality >> warehouse