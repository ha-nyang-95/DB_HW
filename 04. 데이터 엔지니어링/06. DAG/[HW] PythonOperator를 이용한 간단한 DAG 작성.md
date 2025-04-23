# PythonOperator를 이용한 간단한 DAG 작성


📘 1. 실습 주제 개요
==============

### 🧩 주제: Apache Airflow의 PythonOperator를 활용한 DAG(Task 흐름 제어) 구성 실습

현대의 데이터 파이프라인에서 자동화된 워크플로우 관리는 필수적인 요소로 자리 잡고 있다. Apache Airflow는 이러한 워크플로우를 정의하고, 실행하고, 모니터링할 수 있는 플랫폼으로, 특히 **시간 기반의 작업 스케줄링 및 작업 간 의존성 관리**에 강력한 기능을 제공한다.

이번 실습은 \*\*Airflow의 핵심 구조인 DAG(Directed Acyclic Graph)\*\*을 이해하고, 그 안에서 **PythonOperator를 이용해 특정 Python 함수를 주기적으로 실행**하는 기본적인 워크플로우를 구성하는 것을 목표로 한다. 이 실습을 통해 다음과 같은 내용을 학습하게 된다:

<br>

### 🎯 학습 목표

1.  **Airflow DAG 구조 이해**: DAG, Task, Operator의 관계 및 구성 방식 습득
    
2.  **PythonOperator 활용법 습득**: 임의의 Python 함수 실행 구조 학습
    
3.  **스케줄링(Cron 표현식) 개념 학습**: 주기적인 작업 실행 방식 이해
    
4.  **랜덤 로직 기반의 간단한 업무 예시 구현**: 실제로 특정 작업을 자동화할 수 있는 예시 코드를 작성해봄으로써 응용력 향상
    

<br>

### 📌 실무에서의 활용 배경

Airflow는 실무에서 주로 다음과 같은 시나리오에 활용된다:

*   매일 새벽에 **ETL 작업 실행** (예: 데이터 수집, 정제, 저장)
    
*   주기적인 **머신러닝 모델 학습 및 배포**
    
*   이벤트 기반 **알림 또는 데이터 백업 자동화**
    

따라서, 이번 실습은 단순히 과일을 무작위로 선택하는 간단한 로직이지만, 구조적으로는 **실제 업무 자동화의 기본 단위를 학습**하는 데 매우 적합한 출발점이다.

<br>
<br>

🛠️ 2. 코드 구조 및 흐름 해설 + 실행 결과 예시 및 해설
====================================

🔍 코드 구조 요약
-----------

```plaintext
1. 모듈 import
2. DAG 정의 (스케줄, 시작 날짜, 타임존 등 포함)
3. 실행 함수 정의 (과일 선택)
4. PythonOperator로 Task 생성
```

<br>

📂 코드 흐름 해설
-----------

### ✅ ① 필수 모듈 import

```python
from airflow import DAG
import datetime
import pendulum
from airflow.operators.python import PythonOperator
import random
```

*   `DAG`: 워크플로우 전체를 구성하는 기본 단위
    
*   `pendulum`: Airflow에서 시간대를 정확히 지정하기 위해 사용
    
*   `PythonOperator`: Python 함수를 실행하는 Operator
    
*   `random`: 실습 목적을 위한 난수 생성
    

<br>

### ✅ ② DAG 정의

```python
with DAG(
    dag_id="dags_python_operator",
    schedule="30 6 * * *",
    start_date=pendulum.datetime(2021, 1, 1, tz="Asia/Seoul"),
    catchup=False,
) as dag:
```

*   `dag_id`: DAG의 고유 이름 (UI에서도 이 이름으로 표시됨)
    
*   `schedule`: 매일 오전 6시 30분에 실행 (cron 표현식)
    
*   `start_date`: DAG 시작 기준 시간 (한국 시간대 설정)
    
*   `catchup=False`: 과거 날짜에 대해 실행하지 않도록 설정 (백필 방지)
    

<br>

### ✅ ③ Python 함수 정의

```python
def select_fruit():
    fruit = ['APPLE', 'BANANA', 'ORANGE', 'AVOCADO']
    rand_int = random.randint(0, 3)
    print(fruit[rand_int])
```

*   4종류 과일 중 하나를 무작위로 선택하여 출력하는 간단한 함수
    
*   **출력 결과는 Task 실행 시 Airflow의 로그에서 확인 가능**
    

<br>

### ✅ ④ PythonOperator 설정

```python
py_t1 = PythonOperator(
    task_id='py_t1',
    python_callable=select_fruit
)
```

*   `task_id`: DAG 내에서의 Task 이름
    
*   `python_callable`: 실행할 Python 함수 지정
    

> 이 Task는 DAG이 실행될 때마다 `select_fruit()` 함수를 실행하게 된다.

<br>

🖥️ 실행 결과 예시
------------

Airflow UI나 CLI에서 DAG을 실행하거나 특정 날짜를 지정하여 실행할 경우, 다음과 같이 로그에 출력된다:

```
[2025-04-23, 06:30:00] {taskinstance.py:1145} INFO - Running: select_fruit()
[2025-04-23, 06:30:00] INFO - BANANA
```

혹은 다른 실행에서는 다음과 같이 출력될 수 있다:

```
[2025-04-24, 06:30:00] INFO - ORANGE
```

실제 로그에서 `fruit[rand_int]` 값이 어떤지 확인함으로써 함수가 정상적으로 호출되었는지를 검증할 수 있다.

<br>

🔁 실습 구조 요약 흐름도
---------------

```mermaid
graph TD
    A[Airflow Scheduler] --> B[Trigger DAG (6:30 매일)]
    B --> C[PythonOperator 실행]
    C --> D[select_fruit() 함수 호출]
    D --> E[과일 무작위 선택 및 출력 (로그 기록)]
```

<br>
<br>

⚙️ 3. 전체 코드 + 상세 주석
===================

```python
# DAG을 구성하기 위한 Airflow의 기본 모듈 import
from airflow import DAG

# 날짜와 시간 관련 처리를 위한 파이썬 내장 모듈
import datetime

# 타임존을 정확히 지정하기 위해 사용되는 외부 라이브러리
import pendulum

# Python 함수를 Task로 등록할 때 사용하는 Operator
from airflow.operators.python import PythonOperator

# 무작위 선택을 위한 random 모듈
import random

# DAG 정의 시작: with 구문을 통해 DAG 컨텍스트 블록을 선언
with DAG(
    dag_id="dags_python_operator",  # DAG의 이름 (Airflow 웹 UI에서 이 이름으로 표시됨)
    schedule="30 6 * * *",           # 스케줄 주기: 매일 오전 6시 30분에 실행 (Cron 표현식)
    start_date=pendulum.datetime(2021, 1, 1, tz="Asia/Seoul"),  # DAG 실행 시작 시점 및 타임존 설정
    catchup=False,                   # 과거 실행 누락분을 실행하지 않도록 설정 (백필 방지)
) as dag:                            # with 블록 내부에서 DAG에 포함될 Task들을 정의함

    # DAG 안에서 실행될 Python 함수 정의
    def select_fruit():
        fruit = ['APPLE', 'BANANA', 'ORANGE', 'AVOCADO']  # 과일 목록 정의
        rand_int = random.randint(0, 3)  # 0~3 사이의 난수 생성 (인덱스)
        print(fruit[rand_int])  # 랜덤하게 선택된 과일 이름을 출력

    # 위에서 정의한 select_fruit 함수를 실행하는 Task 생성
    py_t1 = PythonOperator(
        task_id='py_t1',            # 이 Task의 이름 (Airflow UI에 표시됨)
        python_callable=select_fruit  # 실행할 함수 지정
    )
```

<br>

📌 코드 실행 시 요약 흐름
----------------

1.  Airflow 스케줄러는 매일 6시 30분에 `dags_python_operator` DAG을 실행
    
2.  DAG 안의 Task `py_t1`이 실행되며, `select_fruit()` 함수가 호출됨
    
3.  함수는 과일 리스트 중 하나를 무작위로 선택하여 출력
    
4.  출력 내용은 Airflow 로그를 통해 확인 가능
    

<br>

💡 참고 포인트
---------

*   DAG의 `catchup=False` 설정은 과거 날짜에 대해 DAG이 자동으로 실행되지 않도록 하여 **불필요한 리소스 낭비를 방지**합니다.
    
*   PythonOperator는 실무에서도 다양한 용도로 활용되며, 예를 들어 **데이터 수집 크롤러 호출**, **S3/DB 작업**, **ML 모델 실행** 등의 태스크를 구성할 수 있습니다.
    

<br>
<br>

📚 4. 추가 설명 및 실무 팁
==================

💡 자주 하는 실수와 주의사항
-----------------

### 1\. `start_date`와 `schedule`의 관계 이해 부족

*   `start_date`는 DAG의 첫 실행 기준 시점이고, `schedule`은 **그 이후부터의 반복 실행 주기**를 의미합니다.
    
*   예를 들어, `start_date=2021-01-01`, `schedule="30 6 * * *"`라면,
    
    *   DAG은 **2021-01-01 06:30 이후부터 매일 06:30에 실행**됨을 의미합니다.
        
*   실수로 `start_date`를 미래로 설정하거나, `catchup=True` 상태에서 과거로 설정하면, **수천 개의 DAG 인스턴스가 몰아서 실행**되는 경우가 있습니다.
    

### 2\. `print()`만 사용하고 로그 확인을 못함

*   Airflow는 출력 결과를 **표준 로그**에 기록합니다.
    
*   따라서 `print()` 결과는 Airflow UI → DAG 실행 기록(Task Instance) → Log 탭에서 확인해야 합니다.
    
*   터미널에서 직접 확인하려면 `airflow tasks test` 명령어를 사용할 수도 있습니다.
    

### 3\. DAG 외부에 Task 선언

*   모든 Task는 `with DAG(...) as dag:` 블록 안에서 정의되어야 합니다.
    
*   블록 바깥에서 정의하면 DAG에 Task가 **등록되지 않음** → UI에서 아무 작업도 보이지 않음
    

<br>

🚀 확장 방향 및 실무 적용 아이디어
---------------------

### 1\. PythonOperator + 외부 API 호출

*   `select_fruit()` 대신 REST API를 호출하거나, DB에 접속하여 데이터를 처리하는 코드로 대체 가능
    
*   예시:
    
    ```python
    import requests
    
    def fetch_weather():
        res = requests.get("https://api.weatherapi.com/...")
        print(res.json())
    ```
    

### 2\. Task 간 의존성 설정 (`>>`, `<<`)

*   여러 개의 Task를 순차적으로 실행하고 싶다면 다음과 같이 연결할 수 있습니다:
    
    ```python
    task1 >> task2 >> task3
    ```
    
*   이는 DAG이 단순히 병렬 실행이 아닌 **의미 있는 작업 흐름**을 갖도록 설계할 수 있게 해줍니다.
    

### 3\. Task 실패/재시도 옵션 추가

*   실무에서는 네트워크/API 장애로 인해 작업이 실패할 수 있습니다.
    
*   `PythonOperator`에 다음과 같은 인자를 추가하면 복원력을 높일 수 있습니다:
    
    ```python
    py_t1 = PythonOperator(
        task_id='py_t1',
        python_callable=select_fruit,
        retries=3,
        retry_delay=datetime.timedelta(minutes=5)
    )
    ```
    

<br>

📘 정리 요약
--------

| 항목 | 설명 |
| --- | --- |
| DAG ID | 워크플로우의 고유 이름 |
| schedule | 주기적 실행을 위한 Cron 표현식 |
| start\_date | DAG의 시작 기준 시점 |
| catchup | 과거 실행 여부 설정 (`False` 권장) |
| PythonOperator | Python 함수를 Task로 실행할 수 있는 방식 |
| 실무 활용 | ETL 자동화, API 호출, DB 백업 등 다양한 작업 자동화 |

<br>

🎓 마무리 조언
---------

본 실습은 매우 단순하지만, Airflow의 핵심 구조인 **DAG, Operator, 스케줄링**의 원리를 이해하는 데 매우 적합한 예제입니다. 실무에서는 DAG 하나에 수십 개의 Task가 연결되며, 다양한 연산, 트리거, 외부 시스템 간 인터페이스가 복합적으로 작동합니다. 이번 실습을 시작점으로 삼아, 점진적으로 BashOperator, BranchPythonOperator, Sensor 등의 고급 개념으로 확장해보는 것이 좋습니다.

