from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "anish",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="crypto_pipeline",
    default_args=default_args,
    description="Crypto Data Pipeline",
    schedule_interval="* * * * *",  # every 1 minute
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["crypto", "pipeline"],
) as dag:

    fetch_data = BashOperator(
        task_id="fetch_data",
        bash_command="python3 /opt/airflow/scripts/fetch_crypto.py"
    )

    load_data = BashOperator(
        task_id="load_data",
        bash_command="python3 /opt/airflow/scripts/load_to_db.py"
    )

    transform_data = BashOperator(
        task_id="transform_data",
        bash_command="psql postgresql://airflow:airflow@postgres/airflow -f /opt/airflow/scripts/transform.sql"
    )

    # Task order
    fetch_data >> load_data >> transform_data