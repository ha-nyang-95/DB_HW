# Airflow에서 실행된 작업의 결과를 파일로 저장하고 검토

📘 1\. 실습 주제 개요
---------------

**주제: Bash 스크립트를 실행하는 단일 Task DAG 구성**

<br>

### 🧠 이론 및 배경

이번 실습에서는 `BashOperator`를 사용하여 **Airflow DAG 내부에서 외부 Bash 스크립트를 직접 실행하는 방법**을 학습합니다. Python이 아닌 시스템 수준의 작업(예: 파일 이동, 데이터 압축, 로그 정리 등)은 Bash 스크립트로 처리하는 경우가 많으며, 이 스크립트를 Airflow로 자동화하면 운영 효율성을 크게 높일 수 있습니다.

<br>

### 💡 핵심 키워드

| 개념 | 설명 |
| --- | --- |
| **DAG (Directed Acyclic Graph)** | Airflow에서 작업 흐름을 정의하는 단위 |
| **BashOperator** | 시스템 명령어나 `.sh` 스크립트를 실행하기 위한 Operator |
| **bash\_command** | 실행할 명령어 또는 스크립트의 경로를 지정하는 인자 |

<br>

### 🎯 실습의 목적

*   Airflow 내에서 Bash 스크립트를 실행하는 자동화 Task를 구성한다.
    
*   BashOperator의 기본 구조와 실행 방식을 익힌다.
    
*   PythonOperator 외에 다양한 Operator를 유연하게 사용하는 방법을 체득한다.
    

<br>

### ❓왜 이걸 배우는가?

실제 데이터 처리 파이프라인에서는 종종 다음과 같은 작업이 요구됩니다:

*   시스템 명령어 실행 (예: 파일 복사, 이동, 삭제)
    
*   데이터 전처리 스크립트 실행 (예: `awk`, `sed`, `grep` 활용)
    
*   사내 서버나 외부 데이터 파이프라인과의 연동 (예: FTP 업로드, 로그 정리)
    

이러한 작업을 Python으로 직접 구현하기보다 Bash 스크립트를 통해 처리하는 것이 더 간결하고 효율적인 경우가 많습니다. 이번 실습은 그러한 실무 사례를 대비한 핵심 기초 학습입니다.

<br>
<br>

🛠️ 2\. 코드 구조 및 흐름 해설 + 실행 결과 예시
--------------------------------

### 🔧 전체 DAG 구성 요약

이 DAG은 단 하나의 작업(Task)만 포함하고 있으며, 해당 작업은 Airflow 내에서 **외부 Bash 스크립트(`process_csv.sh`)를 실행**합니다.

```mermaid
graph TD
    A[bash_dag_process (BashOperator)] --> B[process_csv.sh 실행]
```

<br>

### 🧩 주요 코드 구성 요소 해설

#### 1\. `default_args` 설정

```python
default_args = {
    "start_date": datetime(2025, 4, 29)
}
```

*   DAG의 시작 시간을 정의합니다. 이 날짜 이후로만 DAG이 실행될 수 있습니다.
    
*   `retries`, `retry_delay` 등의 설정을 추가하여 오류 발생 시 재시도 로직을 지정할 수도 있습니다.
    

<br>

#### 2\. DAG 정의

```python
dag = DAG(
    "bash_dag",
    default_args=default_args,
    description="DAG to process using Bash script"
)
```

*   `dag_id`: DAG의 고유 식별자이며, Airflow UI에 표시됩니다.
    
*   `description`: DAG에 대한 간략한 설명입니다.
    
*   `schedule_interval`이 지정되지 않아 수동으로 실행하거나 테스트 실행이 가능하도록 구성되어 있습니다.
    

<br>

#### 3\. BashOperator 정의

```python
process_csv_task = BashOperator(
    task_id="bash_dag_process",
    bash_command="/opt/airflow/plugins/shell/process_csv.sh",
    dag=dag
)
```

*   `task_id`: 이 Task의 고유 이름입니다.
    
*   `bash_command`: 실제 실행할 Bash 명령 또는 `.sh` 스크립트 경로입니다.
    
    *   절대 경로를 사용하는 것이 안정적입니다 (`/opt/airflow/...` 등)
        
    *   Airflow 컨테이너 내부 기준 경로이므로, 호스트 시스템과는 경로가 다를 수 있음에 유의해야 합니다.
        
*   `dag`: 이 Task가 소속된 DAG을 명시합니다.
    

<br>

### ✅ 실행 결과 예시

스크립트 `process_csv.sh`가 다음과 같다고 가정합니다:

```bash
#!/bin/bash
echo "[BASH] CSV 파일 처리 시작"
cat data/input_data.csv | awk -F',' '{print $1}' > data/first_column.txt
echo "[BASH] 첫 번째 컬럼 추출 완료"
```

Airflow 로그에는 다음과 같은 출력이 나타납니다:

```
[2025-05-11, 16:30:00] Starting task: bash_dag_process
[BASH] CSV 파일 처리 시작
[BASH] 첫 번째 컬럼 추출 완료
```

*   `.csv` 파일이 존재하지 않거나 경로가 잘못된 경우, 로그에 `No such file or directory` 등의 오류가 발생합니다.
    
*   이는 DAG 실패로 이어지며, Airflow UI에서 상태가 `failed`로 표시됩니다.
    

<br>
<br>


⚙️ 3\. 전체 코드 + 상세 주석
--------------------

```python
# ----------------------------------------
# (0) 라이브러리 임포트
# ----------------------------------------
from airflow import DAG  # DAG 객체 생성: 작업 흐름의 뼈대 역할
from airflow.operators.bash import BashOperator  # Bash 명령어 또는 스크립트를 실행할 수 있는 Operator
from datetime import datetime, timedelta  # 날짜/시간 설정을 위한 모듈

# ----------------------------------------
# (1) DAG의 기본 설정 정의
# ----------------------------------------
default_args = {
    "start_date": datetime(2025, 4, 29),  # DAG이 처음 실행 가능한 날짜 설정
    # "retries": 1,                      # (선택 사항) 실패 시 재시도 횟수 지정 가능
    # "retry_delay": timedelta(minutes=5)  # (선택 사항) 재시도 간 대기 시간 설정 가능
}

# ----------------------------------------
# (2) DAG 정의
# ----------------------------------------
dag = DAG(
    "bash_dag",  # DAG의 고유 ID (Airflow UI에서 이 이름으로 표시됨)
    default_args=default_args,  # 기본 설정 적용
    description="DAG to process using Bash script",  # DAG 설명
    schedule_interval=None  # (선택) 정기 실행 없이 수동 실행만 허용
)

# ----------------------------------------
# (3) BashOperator Task 정의
# ----------------------------------------
process_csv_task = BashOperator(
    task_id="bash_dag_process",  # Task의 고유 ID (Airflow에서 추적 및 로그 확인용)
    bash_command="/opt/airflow/plugins/shell/process_csv.sh",  # 실행할 Bash 스크립트의 경로
    dag=dag  # 해당 Task가 소속된 DAG 지정
)

# ----------------------------------------
# (4) DAG 내 실행 순서 정의
# ----------------------------------------
process_csv_task  # 단일 Task이므로 추가 연결 없이 실행만 등록하면 됨
```

<br>

### 📁 실습 구조 예시

실제 프로젝트 폴더 구조는 다음과 같아야 합니다:

```
airflow/
├── dags/
│   └── bash_dag.py              ← 위 코드 파일
├── plugins/
│   └── shell/
│       └── process_csv.sh       ← 실행할 Bash 스크립트
├── data/
│   └── input_data.csv           ← 처리 대상 CSV 파일
```

Airflow는 기본적으로 `/opt/airflow`를 루트 경로로 삼기 때문에 상대 경로보다는 **절대 경로 기반 구성**이 실무에서 더 안정적입니다.

<br>
<br>


📚 4\. 추가 설명 및 실무 팁
-------------------

### ✅ 실무 활용 예시

| 사용 시나리오 | 설명 |
| --- | --- |
| 💾 **데이터 수집 및 이동** | 외부 시스템에서 scp, wget 등을 통해 주기적으로 데이터 파일을 내려받거나 이동시킴 |
| 🧹 **임시 파일 정리** | 오래된 로그, 캐시 파일, 중간 결과 등을 cron처럼 자동으로 정리 |
| 📦 **압축 및 백업** | 매일 자정에 디렉토리를 tar로 묶고 백업 디렉토리로 이동 |
| 🔗 **외부 시스템 호출** | bash로 FTP 업로드, rsync, cURL, ssh 접속 등 실행 가능 |

<br>

### ⚠️ 자주 발생하는 실수 및 주의사항

#### 1\. 경로 문제 (`No such file or directory`)

*   Airflow는 \*\*자체 실행 환경(예: Docker 컨테이너)\*\*에서 작동하므로,  
    호스트 OS 기준의 경로와 실행 컨테이너 내부의 경로가 일치하지 않을 수 있습니다.
    
*   BashOperator에서는 항상 **실행 가능한 경로에 스크립트를 두고, 절대 경로**를 사용하는 것이 안전합니다.
    

#### 2\. 실행 권한 누락 (`Permission denied`)

*   `.sh` 파일에 실행 권한이 없으면 DAG이 실패합니다.
    
*   다음 명령어로 사전에 권한을 부여해야 합니다:
    

```bash
chmod +x process_csv.sh
```

#### 3\. 스크립트 내부 로그 출력 확인

*   Airflow 웹 UI의 로그 탭에서 `echo` 출력 내용을 확인 가능
    
*   실시간 디버깅을 위해 스크립트에 충분한 로그 메시지(`echo`)를 삽입하는 것이 좋습니다
    

<br>

### 🔄 확장 및 심화 방향

#### 1\. 여러 BashOperator로 Task 분리

```python
extract_task = BashOperator(task_id="extract", bash_command="sh extract.sh", dag=dag)
transform_task = BashOperator(task_id="transform", bash_command="sh transform.sh", dag=dag)
load_task = BashOperator(task_id="load", bash_command="sh load.sh", dag=dag)

extract_task >> transform_task >> load_task
```

*   하나의 `.sh`에 모든 로직을 넣기보다, **ETL 단계별 스크립트 분리**로 구조화 가능
    

#### 2\. PythonOperator와 조합

*   PythonOperator로 데이터를 가공한 후, BashOperator로 결과를 전송
    
*   또는 반대로 Bash에서 데이터를 전처리하고, Python에서 ML 모델 적용
    

#### 3\. BashOperator + Template 활용

```python
bash_command="sh process.sh {{ ds }}"
```

*   Jinja 템플릿 문법으로 실행일자, 파라미터 등을 스크립트에 동적으로 주입 가능
    

<br>

### ✏️ 연습 과제 제안

1.  `.sh` 스크립트에서 파일 존재 여부를 확인한 후 조건 분기하도록 만들어보기
    
2.  `bash_command="echo {{ ds }}"`로 실행일자를 로그에 찍어보기
    
3.  `BranchPythonOperator`와 결합하여 조건에 따라 다른 `.sh`를 실행해보기
    
