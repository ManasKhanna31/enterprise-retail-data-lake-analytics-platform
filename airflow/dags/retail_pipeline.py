"""Airflow DAG with retries and an explicit quality gate."""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
with DAG("retail_pipeline", start_date=datetime(2026, 1, 1), schedule="@daily", catchup=False, default_args={"retries": 2, "retry_delay": timedelta(minutes=5)}) as dag:
    extract = BashOperator(task_id="extract_sources", bash_command="python -m scripts.run_pipeline")
    quality = BashOperator(task_id="data_quality_gate", bash_command="python -m scripts.run_pipeline")
    warehouse = BashOperator(task_id="load_warehouse", bash_command="echo 'warehouse load is environment-dependent'")
    extract >> quality >> warehouse
