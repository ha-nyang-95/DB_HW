# PyFlink 환경 구축 방법

🔁 PyFlink 과제 복습 가이드 (비전공자용)
============================

🧠 목표
-----

> CSV 파일의 금융 거래 데이터를 읽어서 거래유형별로 합계 금액을 구하고 출력하는 PyFlink 프로그램 만들기

* * *

🛠️ 1단계: 환경 구축
--------------

### 1-1. 터미널에서 작업 폴더 만들기

```bash
mkdir ~/pyflink_hw
cd ~/pyflink_hw
```

### 1-2. 가상환경 만들기 (Python 전용 공간)

```bash
python3 -m venv venv
source venv/bin/activate
```

> ✅ 가상환경이 활성화되면 `(venv)`가 터미널 앞에 뜸

### 1-3. 필요한 패키지 설치

```bash
pip install pandas apache-flink
```

혹시 `requirements.txt`가 있다면 아래처럼 설치

```bash
pip install -r requirements.txt
```

* * *

📦 2단계: Flink 설치 & 실행
---------------------

### 2-1. Flink 압축 풀기 (이미 풀려있다면 건너뛰기)

```bash
tar -xvzf flink-1.20.0-bin-scala_2.12.tgz
```

### 2-2. Flink 실행

```bash
cd flink-1.20.0
./bin/start-cluster.sh
```

> 브라우저에서 http://localhost:8081 접속 → 클러스터 대시보드 보이면 성공!

* * *

📂 3단계: CSV 준비 & 코드 작성
----------------------

### 3-1. CSV 파일 예시 (`data.csv`)

```csv
transaction_type,amount
deposit,1000
withdrawal,500
deposit,200
withdrawal,100
```

### 3-2. 코드 파일 작성 (`skeleton.py`)

```python
import pandas as pd
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common.typeinfo import Types

def main():
    # Flink 실행 환경 설정
    env = StreamExecutionEnvironment.get_execution_environment()

    # CSV 불러오기
    df = pd.read_csv("./data.csv")
    transactions = df[["transaction_type", "amount"]].dropna().values.tolist()

    # 데이터 타입 정의
    type_info = Types.TUPLE([Types.STRING(), Types.FLOAT()])

    # 리스트 데이터를 Flink 스트림으로 변환
    transaction_stream = env.from_collection(transactions, type_info=type_info)

    # 거래유형별로 그룹화하고 금액 합계 계산
    total_amount_per_type = (
        transaction_stream
        .key_by(lambda x: x[0])  # 거래유형별 그룹화
        .sum(1)                  # 금액 합계
    )

    # 결과 출력
    total_amount_per_type.print()

    # Flink 실행
    env.execute("Streaming Transaction Processing")

if __name__ == "__main__":
    main()
```

> 📌 주의: `data.csv`는 `skeleton.py`와 같은 폴더에 있어야 함!

* * *

▶️ 4단계: 코드 실행
-------------

```bash
python skeleton.py
```

### ✅ 실행 결과 예시

```bash
(deposit, 1200.0)
(withdrawal, 600.0)
```

* * *

❓ 핵심 개념 설명 (진짜 쉽게)
------------------

| 용어 | 쉽게 설명하면? |
| --- | --- |
| `pandas.read_csv()` | 엑셀처럼 생긴 파일(CSV)을 파이썬에서 읽음 |
| `dropna()` | 비어있는 행은 빼고 |
| `values.tolist()` | 데이터를 리스트로 바꿈 (Flink가 처리할 수 있도록) |
| `from_collection()` | Flink가 데이터를 스트림으로 이해할 수 있게 만듦 |
| `key_by(lambda x: x[0])` | 거래유형(예: deposit, withdrawal) 기준으로 묶음 |
| `sum(1)` | 각 그룹의 금액을 더함 (1번 인덱스는 amount) |
| `print()` | 결과를 화면에 보여줌 |
| `execute()` | 지금까지 한 걸 실제로 실행함 |

* * *

🧹 5단계: 마무리 및 종료
----------------

### Flink 클러스터 종료

```bash
./bin/stop-cluster.sh
```

### 가상환경 종료

```bash
deactivate
```

* * *

📁 최종 폴더 구조 예시
--------------

```
pyflink_hw/
│
├── venv/               ← 가상환경
├── flink-1.20.0/       ← Flink
├── data.csv            ← 거래 데이터
└── skeleton.py         ← 실행 코드
```

* * *

🧠 마무리 팁
--------

*   **처음부터 다시 할 땐**: `venv`, `data.csv`, `skeleton.py`만 준비하면 돼요.
    
*   **자주 실행 안 되는 경우**: 파일 경로가 잘못되었거나, 가상환경이 꺼진 상태일 수 있음.
    
*   **웹 UI 확인**: `http://localhost:8081`로 Flink 상태 확인 가능.
    

* * *

필요하면 이 내용을 PDF나 Markdown 파일로 정리해드릴 수도 있어요!  
또한, 이후에 Kafka, Prometheus, Grafana를 붙여서 분석까지 가고 싶으시면 알려주세요 😊



---
Powered by [ChatGPT Exporter](https://www.chatgptexporter.com)