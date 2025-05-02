from airflow import DAG
from airflow.decorators import task
from airflow.operators.bash import BashOperator
import pendulum

with DAG(
    dag_id="python_bash_xcom_with_task_decorator",
    start_date=pendulum.datetime(2024, 3, 1, tz="Asia/Seoul"),
    catchup=False,
) as dag:

    @task
    def push_xcom_value():
        return "Hello from @task!"

    msg = push_xcom_value()

    pull_task = BashOperator(
        task_id="pull_task",
        bash_command="echo '{{ ti.xcom_pull(task_ids=\"push_xcom_value\") }}'",
    )

    msg >> pull_task
