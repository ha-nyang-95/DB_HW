# 고급 DAG 작성 및 데이터 공유
## Xcom과 Variable을 활용한 데이터 전달
### Xcom이란?
### Xcom을 이용한 데이터 전달 원리
#### Xcom 데이터 저장(xcom_push)
#### Xcom 데이터 조회(xcom_pull)
### Xcom 사용 방법
### PythonOperator with Xcom
(1_dags_Xcom.py)
### BashOperator with Xcom
(2_dags_bash_xcom.py)
### Python&BashOperator with Xcom
(3_1_python_bash_xcom_decorator.py)
(3_python_bash_xcom.py)
### 전역 공유 변수(Variable)란?
### 전역 공유 변수(Variable) 등록하기
Webserver에 접속하고, [Admin] -> [Variable] 클릭
[+] 클릭해서 새로운 Variable 생성
Key, value 값 입력하고 [save] 클릭
### 전역 공유 변수(Variable) 사용하기
Variable 라이브러리의 get 함수를 사용하여 값 사용
var.value에 꺼내고 싶은 key 값을 입력
(4_dags_var.py)
### 전역 공유 변수(Variable) vs Xcom
Xcom은 Task간 데이터 전달용, Variable은 DAG 실행 간 설정값 저장용으로 사용됨
DAG 실행 단위로 데이터를 유지하고 싶으면 Xcom, 모든 DAG에서 공통으로 사용할 데이터를 저장하려면 Variable 사용

## Branching과 Trigger Rule
### BranchOperator란?
Airflow에서 DAG 실행 흐름을 조건에 따라 분기할 수 있도록 하는 오퍼레이터
### BranchOperator
#### BranchPythonOperator
#### BranchDagRunOperator
### 조건 기반 실행 흐름
(5_dags_branch.py)
### API 응답값 기반으로 분기 처리 방식
(6_dags_api_test.py)
### Trigger Rule(트리거 규칙)
Task가 실행되기 위한 조건을 설정하는 기능
all_success(기본값)
all_failed
all_done
one_failed
one_success
none_failed
none_failed_or skipped
none_skipped

## External Task Sensor 개념
### TaskGroup이란?
DAG 내에서 여러 Task를 그룹화하여 논리적으로 관리하는 기능
### TaskGroup 활용법
(7_task_group.py)
### TaskGroup 정리
목적
성능
병렬 실행
UI 표현 방식
의존성 관리
실행 방식
### ExternalTaskSensor
### ExternalTaskSensor 활용법
(8_dags_external_producer.py)
(9_dags_external_consumer.py)
### Dynamic DAG란?
DAG를 정적으로 정의하는 것이 아니라, 실행 시점에 동적으로 생성하는 방식
### Dynamic DAG 활용법
#### Task 목록을 리스트로 받아 반복문으로 Task 생성
(10_dags_dynamic.py)

## Airflow Connections 및 Hooks 소개
### Airflow Connection & Hook
#### Connection
#### Hook
#### Web UI Connection 설정
(11_dags_hook_test.py)
(## 12. airflow connection & hook (Postgres))







1. XCom과 Variable을 활용한 데이터 전달
1-1. XCom이란?
XCom의 개념과 역할

XCom vs Variable: 언제 어떤 것을 써야 하나?

1-2. XCom 사용 방법
xcom_push를 통한 데이터 저장

xcom_pull을 통한 데이터 조회

PythonOperator를 활용한 예시: 1_dags_Xcom.py

BashOperator를 활용한 예시: 2_dags_bash_xcom.py

Python ↔ Bash 간 데이터 전달 예시

3_python_bash_xcom.py

3_1_python_bash_xcom_decorator.py

1-3. Variable(전역 공유 변수) 사용하기
Variable의 개념과 역할

Variable 등록 절차 (Web UI 기준)

Variable 접근 방법 (Variable.get() 사용법)

예제 DAG: 4_dags_var.py

2. 조건 분기와 실행 조건 제어
2-1. 분기(Branching)란?
DAG 흐름 제어: Branching의 필요성과 개념

BranchPythonOperator / BranchDagRunOperator 개요

2-2. 조건 기반 분기 처리 예시
조건에 따른 태스크 실행 흐름 제어: 5_dags_branch.py

API 응답값에 따른 분기 처리: 6_dags_api_test.py

2-3. Trigger Rule(트리거 규칙)이란?
기본 규칙: all_success

그 외 규칙 정리:

all_failed, all_done, one_failed, one_success

none_failed, none_failed_or_skipped, none_skipped

3. TaskGroup과 외부 DAG 연동
3-1. TaskGroup이란?
TaskGroup의 필요성과 기능

예제 DAG: 7_task_group.py

TaskGroup의 장점 요약:

목적

병렬 실행

UI 표현 개선

실행 흐름 관리

3-2. 외부 DAG 연동 (ExternalTaskSensor)
ExternalTaskSensor의 개념

외부 DAG의 특정 Task 완료 여부 감지

예제 DAG:

생산자 DAG: 8_dags_external_producer.py

소비자 DAG: 9_dags_external_consumer.py

4. 동적 DAG (Dynamic DAG)
4-1. 동적 DAG이란?
정적 DAG vs 동적 DAG

실행 시점에 DAG을 구성하는 이유

4-2. 동적 Task 생성 방식
Task 목록을 리스트로 받아 반복문으로 생성

예제 DAG: 10_dags_dynamic.py

5. Airflow Connections 및 Hook
5-1. Connection과 Hook 개념 정리
Connection: 외부 시스템에 대한 설정 정보

Hook: Connection을 사용하여 작업을 수행하는 도구

5-2. Web UI에서 Connection 설정하기
설정 절차: Admin → Connections → [+] 등록

예제 DAG: 11_dags_hook_test.py

5-3. PostgreSQL 연결을 통한 예제
실습 DAG: 12_airflow_connection_postgres.py (제목 유추됨)

