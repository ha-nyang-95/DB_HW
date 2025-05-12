from airflow import DAG
from airflow.operators.empty import EmptyOperator
from datetime import datetime, timedelta

dag_a = DAG(
    dag_id="dag_a",
    start_date=datetime(2025, 3, 1),
)

task_a = EmptyOperator(
    task_id="task_a",
    dag=dag_a
)

