# Airflow DAG 기초 및 Task 연결
## Airflow DAG 기본 구조
### DAG란?
Airflow에서 Task간 실행 순서를 정의하는 핵심 구조
(1_dags_bash_operator.py 참고)
### Task란?
Task는 워크플로우를 구성하는 개별 작업 단위
특정 연산을 수행하는 Operator를 사용하여 정의(BashOperator, PythonOperator, SQLExecuteOperator...)
DAG 내에서 하나의 노드(Node)로 존재하며, 특정한 작업(데이터 처리, API 호출, SQL 실행 등)을 수행
Task는 서로 의존성을 설정하여, 순차적 실행(Sequentail) 또는 병렬 실행(Parellel)이 가능함
재시도(Retry) 및 실행 시간 제한 설정 가능
### Task LifeCycle

## Task 및 Operator 개념
### Task 주요 속성
task_id
operator
depends_on_past
retries
execution_timeout
start_date
end_date
schedule_interval
priority_weight
task_concurrency
### 오퍼레이터(Operator)란?
### 오퍼레이터(Operator) 종류
Action Operators
Sensor Operators
Transfer Operators
Database Operators
Big Data & ML Operators
Docker & Kuberneres Operators
Dummy Operators

## PythonOperator, BashOperator, DummyOperator 개요
### Action Operators
#### BashOperator
(2_bashOperator.py 참고)
#### BashOperators로 컨테이너 외부의 쉘 스크립트 수행
("11. shell script" 참고)
(select_fruit.sh, 3_bash_select.py 참고)
#### EmailOperator
("10. EmailOperator 사용을 위한 SMTP 설정" 참고)
#### EmailOperator - 구글 계정 설정
(4_dags_email_operator.py 참고)
#### PythonOperator
(5_dags_python_operator.py 참고) 
### EmptyOperator
Task 실행 없이 DAG 구조를 설정하는데 사용됨
DAG의 논리적 흐름을 구성하는 용도로 활용
(6_dags_empty_operator.py 참고)

## DAG Scheduling 및 Trigger 개념
### DAG내 Task간 의종성(Dependency)이란?
### Task 연결 원리
### Task 종류
Upstream Task
Downstream Task
Linear Dependency
Branching
Parallel Execution
### 기본 연결(순차 실행)
task_1>>task_2 # task_1이 완료된 후 task_2 실행
(7_dags_basic.py 참고)
### 다중 Task 연결(병렬 실행)
task_1>>[task_2, task_3] # task_1 실행 후 task_2와 task_3 병렬 실행
(8_dags_multiple.py 참고)
### 다중 Task 종속 단계
(9_dags_parallel.py 참고)
### Trigger Rule(트리거 규칙)
Task가 실행되기 위한 조건을 설정하는 기능
기본적으로 모든 Upstream Task가 성공해야 실행됨(all_success)
특정 Task의 실행 결과에 따라 실행 조건을 다르게 설정할 수 있음

all_success(기본값)
all_failed
all_done
one_failed
one_success
none_failed
none_failed_or_skipped
none_skipped
### Trigger Rule(트리거 규칙) 예시
(10_dags_trigger.py 참고)


## Cron 스케줄링 및 Task 연결 방법
### DAG 스케줄
### start_date
### execution date
### execution date 예시
### schedule_interval(스케줄 간격)
### schedule_interval(스케줄 간격) 설정 방법
### Cron Schedule 표현
### 빈도 설정
### Catchup 이란?
자동복구기능
### Backfull이란?
수동복구기능