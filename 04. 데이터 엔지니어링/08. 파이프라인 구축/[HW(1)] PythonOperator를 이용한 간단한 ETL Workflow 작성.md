# PythonOperator를 이용한 간단한 ETL Workflow 작성

📘 1\. 실습 주제 개요
---------------

**주제: CSV 파일을 Pandas로 변환하고 저장하는 단일 Task DAG 구성**

<br>

### 🧠 이론 및 배경

데이터 분석 업무에서 가장 기본적이면서도 반복적으로 수행되는 작업 중 하나는 **CSV 파일의 읽기–가공–저장**입니다. 이 작업이 정기적으로 발생한다면, 이를 자동화하여 수작업을 줄이는 것이 매우 중요합니다. 이번 실습은 이러한 목적을 달성하기 위한 워크플로우를 **Airflow DAG**으로 구성합니다.

핵심 키워드는 다음과 같습니다:

| 개념                             | 설명                                                                   |
| -------------------------------- | ---------------------------------------------------------------------- |
| **DAG (Directed Acyclic Graph)** | Airflow에서 정의하는 작업 흐름 단위. Task 간 실행 순서를 정의함        |
| **PythonOperator**               | 사용자가 정의한 Python 함수를 Task로 등록하여 실행할 수 있는 Operator  |
| **Pandas**                       | CSV 파일 처리 및 데이터 프레임 조작을 위한 필수 데이터 처리 라이브러리 |

<br>

### 🎯 실습의 목적

*   단일 Python Task로 **CSV 파일을 자동으로 처리하는 DAG**를 구성한다.
    
*   `Pandas`를 통해 **컬럼 이름 변경, 날짜 추가** 등 실질적인 데이터 변환 과정을 포함한다.
    
*   DAG 구조와 Task 등록 방식, 실행 흐름을 익히며 **Airflow의 기초 개념과 작동 방식을 학습**한다.
    

<br>

### ❓왜 이걸 배우는가?

대부분의 데이터 분석 프로젝트는 외부 데이터(대개는 CSV 형태)에서 시작됩니다. 실무에서 이 데이터를 주기적으로 불러오고, 변환하며, 후속 분석이나 모델 학습에 연결해야 할 경우가 많은데, 이를 매번 수동으로 수행하는 것은 비효율적입니다. 따라서 **Airflow 기반 자동화**를 통해 이 과정을 효율화하면, **데이터 엔지니어링 역량**을 실무에 적용할 수 있는 기초를 마련할 수 있습니다.

<br>
<br>

🛠️ 2\. 코드 구조 및 흐름 해설 + 실행 결과 예시
--------------------------------

### 🔧 전체 흐름 요약

이 DAG의 구성은 매우 단순합니다. 오직 하나의 Task(`csv_transform_task`)만 존재하며, 해당 Task는 다음과 같은 과정을 수행합니다:

1.  지정된 경로에서 CSV 파일을 읽고
    
2.  데이터를 변환한 후
    
3.  다시 다른 경로에 저장합니다.
    

즉, DAG 전체가 단일 Python 함수 `transform_csv()`에 의해 수행되는 구조입니다.

<br>

### 🧩 주요 코드 구성 요소 해설

#### 1\. CSV 경로 설정

```python
CSV_FILE_PATH = "data/input_data.csv"
OUTPUT_FILE_PATH = "data/output_data.csv"
```

*   변환 대상과 저장 대상이 되는 파일 경로를 지정합니다.
    
*   이 파일들은 일반적으로 Airflow 프로젝트 디렉토리 내에서 상대 경로로 관리됩니다.
    
*   실제 운영 환경에서는 **S3**, **GCS**, 또는 **DB 연결**로 확장할 수 있습니다.
    

<br>

#### 2\. transform\_csv 함수

```python
def transform_csv():
    df = pd.read_csv(CSV_FILE_PATH)
    df.rename(columns={"old_column": "new_column"}, inplace=True)
    df["processed_date"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    df.to_csv(OUTPUT_FILE_PATH, index=False)
```

*   `read_csv`: 지정된 파일에서 CSV 데이터를 읽어옵니다.
    
*   `rename`: 예제에서는 `"old_column"`이라는 기존 컬럼명을 `"new_column"`으로 변경합니다.
    
*   `processed_date`: 현재 날짜와 시간을 `"YYYY-MM-DD HH:MM:SS"` 형식으로 추가합니다.
    
*   `to_csv`: 최종 데이터를 새 CSV 파일로 저장합니다.
    

📌 **비고**: 컬럼명이 존재하지 않거나 파일이 없으면 에러가 발생하므로, 운영 시 유효성 검사가 중요합니다.

<br>

#### 3\. DAG 및 Task 정의

```python
dag = DAG(...)
transform_task = PythonOperator(...)
```

*   `dag`: 워크플로우의 전체 틀입니다. `dag_id`, `start_date` 등 기본 메타정보를 설정합니다.
    
*   `transform_task`: Python 함수를 실행할 단일 Task입니다. `python_callable`에 지정한 함수가 실행됩니다.
    

<br>

### ✅ 실행 결과 예시

가령, 다음과 같은 CSV 파일이 있다고 가정합니다 (`input_data.csv`):

| old\_column |
| ----------- |
| value1      |
| value2      |

변환 후, `output_data.csv`는 다음과 같은 형태가 됩니다:

| new\_column | processed\_date     |
| ----------- | ------------------- |
| value1      | 2025-05-11 15:45:23 |
| value2      | 2025-05-11 15:45:23 |

*   `old_column`이 `new_column`으로 바뀌었고,
    
*   새로운 날짜 컬럼이 추가되어 저장된 것을 확인할 수 있습니다.
    

<br>
<br>

⚙️ 3\. 전체 코드 + 상세 주석
--------------------

```python
# ----------------------------------------
# (0) 필요한 라이브러리 임포트
# ----------------------------------------
from airflow import DAG  # DAG(워크플로우)를 정의하는 데 사용하는 핵심 객체
from airflow.operators.python import PythonOperator  # Python 함수를 Task로 등록할 수 있는 Operator
from datetime import datetime, timedelta  # 시간 관련 작업에 필요한 모듈
import pandas as pd  # 데이터 프레임 형태로 CSV 파일을 다루기 위한 라이브러리

# ----------------------------------------
# (1) CSV 파일 경로 정의
# ----------------------------------------
CSV_FILE_PATH = "data/input_data.csv"  # 변환할 원본 CSV 파일 경로
OUTPUT_FILE_PATH = "data/output_data.csv"  # 변환 후 저장될 CSV 파일 경로

# ----------------------------------------
# (2) CSV 변환을 수행하는 사용자 정의 함수
# ----------------------------------------
def transform_csv():
    """
    CSV 파일을 읽고 컬럼명을 변경한 후, 새로운 컬럼(processed_date)을 추가하여
    결과를 다른 CSV 파일로 저장하는 함수입니다.
    """

    # CSV 파일 읽기 (Pandas DataFrame으로 로드)
    df = pd.read_csv(CSV_FILE_PATH)

    # 컬럼명 변경 (예: 'old_column' → 'new_column')
    df.rename(columns={"old_column": "new_column"}, inplace=True)

    # 현재 시간 정보를 'processed_date' 컬럼으로 추가
    df["processed_date"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 변환된 결과를 새로운 CSV 파일로 저장
    df.to_csv(OUTPUT_FILE_PATH, index=False)  # index=False: 행 번호는 저장하지 않음

    # 로그 출력 (Airflow 웹 UI 로그에서 확인 가능)
    print("Data transformation complete. Saved to", OUTPUT_FILE_PATH)

# ----------------------------------------
# (3) DAG 기본 설정 (예: 시작 시각)
# ----------------------------------------
default_args = {
    "start_date": datetime(2025, 4, 29),  # DAG 실행을 시작할 기준 시각
    # "retries": 1,                      # (선택) 실패 시 재시도 횟수 설정 가능
    # "retry_delay": timedelta(minutes=5)  # (선택) 재시도 간 간격
}

# ----------------------------------------
# (4) DAG 정의
# ----------------------------------------
dag = DAG(
    dag_id="csv_transform",  # DAG의 고유 ID (Airflow UI에서 표시됨)
    default_args=default_args,  # 위에서 정의한 실행 조건 적용
    description="assignment2",  # DAG에 대한 간단한 설명
    schedule_interval=None  # (선택) 정기 실행하지 않고 수동 실행만 허용
)

# ----------------------------------------
# (5) PythonOperator를 통해 Task 등록
# ----------------------------------------
transform_task = PythonOperator(
    task_id="csv_transform_task",  # 이 Task의 ID (Airflow UI에서 확인 가능)
    python_callable=transform_csv,  # 실행할 Python 함수 연결
    dag=dag  # 이 Task가 속한 DAG 지정
)

# ----------------------------------------
# (6) 실행 흐름 정의 (단일 Task이므로 별도 의존 관계는 없음)
# ----------------------------------------
transform_task  # DAG 내에서 등록만 하면 자동으로 실행 흐름으로 인식됨
```

<br>
<br>

📚 4\. 추가 설명 및 실무 팁
-------------------

### ✅ 실무 활용 예시

| 사용 시나리오                  | 설명                                                            |
| ------------------------------ | --------------------------------------------------------------- |
| 💼 **일간 데이터 정제 자동화**  | 매일 수집되는 CSV 로그 파일을 읽고 포맷을 맞춘 후 저장하는 용도 |
| 📊 **정제 후 시각화 도구 연동** | 변환된 파일을 Tableau, Power BI, Looker Studio 등으로 연동 가능 |
| 🧪 **모델 학습 전 데이터 가공** | 머신러닝 모델에 입력할 데이터셋 전처리 단계를 DAG으로 관리 가능 |

<br>

### ⚠️ 자주 발생하는 실수 및 주의점

#### 1\. 경로 문제 (`FileNotFoundError`)

*   상대 경로(`data/input_data.csv`)로 지정된 파일이 실제로 존재하지 않으면 DAG 실행이 실패합니다.
    
*   Airflow 작업 디렉토리 기준으로 파일 경로를 정확히 설정해야 하며, **로컬 실행과 Airflow 실행 경로가 다를 수 있음**에 주의해야 합니다.
    

#### 2\. 컬럼 이름 오타 (`KeyError`)

*   `rename()`에서 `"old_column"`이 실제 CSV에 존재하지 않으면 에러가 발생합니다.
    
*   변환 전 `df.columns`를 출력하거나 사전 검사하는 로직을 추가하는 것이 안전합니다.
    

#### 3\. 시간 형식 통일 문제

*   `processed_date`는 문자열 형식으로 저장되므로, 후속 처리에서 `datetime`으로 파싱해야 할 수 있습니다.
    
*   저장 시 `"ISO 8601"` 형식 (`.isoformat()`)으로 통일하거나, 후처리 스크립트에서 명시적 변환을 고려해야 합니다.
    

<br>

### 🧠 확장/심화 방향

#### 1\. **매일 자동 실행 설정**

```python
schedule_interval='@daily'
```

*   DAG을 매일 새벽 1시에 자동 실행하도록 설정 가능
    
*   예: `"0 1 * * *"`는 매일 1시 실행
    

#### 2\. **파일 유효성 검사 추가**

```python
if not os.path.exists(CSV_FILE_PATH):
    raise FileNotFoundError("CSV 파일이 존재하지 않습니다.")
```

*   DAG 실패를 방지하거나, 실패 시 명확한 에러 메시지를 제공
    

#### 3\. **Airflow Variable 또는 XCom 활용**

*   CSV 경로를 하드코딩하지 않고, 변수로 관리하거나 이전 Task 결과를 기반으로 경로를 동적으로 생성 가능
    
*   `Variable.get("input_path")`, `kwargs["ti"].xcom_pull(...)` 등
    

#### 4\. **S3 / GCS 연동**

*   Pandas의 `read_csv("s3://bucket-name/path.csv")` 등으로 확장하면 클라우드 환경에서도 동일한 구조 사용 가능
    
*   `boto3`나 `gcsfs`와 함께 사용하면 더욱 견고한 아키텍처로 확장 가능
    

<br>

### ✏️ 연습 과제 제안

1.  **날짜별 파일 처리**: `input_2025-05-11.csv` 형식의 파일명을 자동으로 처리하도록 만들어보기
    
2.  **다중 컬럼 처리 로직 추가**: 여러 개의 컬럼을 동시에 변환하거나, 결측치 제거까지 포함한 전처리 로직 구성
    
3.  **변환 후 알림 추가**: Slack API 또는 이메일 전송으로 성공 여부 알림 기능 구현
    
