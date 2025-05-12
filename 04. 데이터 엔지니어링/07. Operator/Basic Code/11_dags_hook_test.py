from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.hooks.postgres_hook import PostgresHook
from datetime import datetime
import pendulum


'''
Connection 등록 (필수)
PostgresHook(postgres_conn_id="my_postgres_conn") 이 코드가 작동하려면
해당 Connection ID(my_postgres_conn)가 Airflow Web UI > Admin > Connections에 사전에 등록되어 있어야 합니다.
'''

# Postgres 데이터 조회 함수
def fetch_postgres_data():
    hook = PostgresHook(postgres_conn_id="my_postgres_conn")
    df = hook.get_pandas_df(sql="SELECT * FROM news_article LIMIT 10")
    print("조회된 행 수:", len(df))
    print(df.head())

# DAG 정의
with DAG(
    dag_id="postgres_hook_python_operator",
    start_date=pendulum.datetime(2024, 3, 1, tz="Asia/Seoul"),
    schedule_interval="@daily",
    catchup=False,
    tags=["postgres", "hook", "no-task-decorator"]
) as dag:

    fetch_data_task = PythonOperator(
        task_id="fetch_postgres_data",
        python_callable=fetch_postgres_data
    )

    fetch_data_task
