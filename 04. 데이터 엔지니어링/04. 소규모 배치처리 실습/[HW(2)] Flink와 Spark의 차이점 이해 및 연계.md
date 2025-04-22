# Flink와 Spark의 차이점 이해 및 연계

📘 1. 실습 주제 개요: PyFlink를 활용한 금융 데이터 집계 분석
=========================================

💡 주제: Flink Table API로 수행하는 섹터별 거래 데이터 집계
------------------------------------------

### 🎯 실습의 목적

본 실습은 **PyFlink를 활용하여 금융 데이터를 배치 처리**하고, **섹터(Sector)별 집계 통계를 계산**하는 것을 목표로 한다. Flink Table API와 SQL을 통해 CSV 파일로부터 데이터를 읽고, 집계 연산 후 다른 파일로 저장하는 일련의 과정을 실습한다.

### 🧠 왜 이걸 배우는가?

*   **대규모 데이터를 SQL로 처리하는 능력**은 데이터 분석 및 엔지니어링의 핵심이다.
    
*   Flink는 고성능 스트리밍 엔진이지만, **배치 처리(Batch Mode)** 또한 지원하며 실무에서는 대용량 CSV, Parquet 등의 파일 기반 분석에도 자주 사용된다.
    
*   이 실습을 통해 Flink Table API의 **DDL 정의, SQL 집계, 파일 I/O 연결**의 전체 흐름을 이해할 수 있다.
    

<br>
<br>

🛠️ 2. 코드 구조 및 흐름 해설 + 실행 결과 예시 및 해설
====================================

✅ 전체 흐름 요약
----------

본 코드는 다음 6단계를 중심으로 작동한다:

1.  **Flink 환경 설정** (배치 모드로 설정)
    
2.  **샘플 CSV 데이터 생성**
    
3.  **소스 테이블 등록 (CSV -> Table)**
    
4.  **싱크 테이블 등록 (결과 Table -> CSV)**
    
5.  **SQL 집계 수행**
    
6.  **집계 결과 출력**
    

<br>

🔍 코드 구조 해설
-----------

### ① Flink 환경 구성 및 설정

```python
env_settings = EnvironmentSettings.in_batch_mode()
table_env = TableEnvironment.create(env_settings)

config = table_env.get_config().get_configuration()
config.set_string("parallelism.default", "1")
```

*   `in_batch_mode()`는 한 번의 고정된 입력 데이터에 대해 처리하는 **배치 모드**를 지정함.
    
*   `parallelism=1`은 실행 시 병렬 처리 수준을 낮춰 **단일 출력 파일 생성**을 유도. 실습 및 로컬 디버깅 시 유용.
    

<br>

### ② CSV 샘플 데이터 생성

```python
def create_sample_csv():
    ...
```

*   `tempfile` 디렉토리에 1000개의 가상 금융 데이터를 생성.
    
*   각 데이터는 다음 필드를 포함:  
    `stock_code`, `sector`, `price`, `volume`, `transaction_date`
    
*   랜덤으로 생성되며, 데이터 분석 실습에 사용될 기초 자료 제공.
    

예시 데이터 (CSV 파일):

```
005930,semiconductor,820133.59,53,2024-03-08
035420,internet,285893.55,184,2024-09-03
000660,biotech,921209.94,745,2024-04-26
...
```

<br>

### ③ 소스 테이블 정의 (CSV → Table)

```sql
CREATE TABLE finance(
    stock_code STRING,
    sector STRING,
    price DOUBLE,
    volume INT,
    transaction_date STRING
) WITH (
    'connector' = 'filesystem',
    'path' = '{input_path}',
    'format' = 'csv',
    'csv.field-delimiter' = ',',
    'csv.ignore-parse-errors' = 'true'
)
```

*   **Table DDL** 문법을 통해 CSV 데이터를 Flink Table로 매핑.
    
*   `csv.ignore-parse-errors` 옵션을 통해 결측값 등 예외 레코드 무시 가능.
    

<br>

### ④ 싱크 테이블 정의 (Table → CSV)

```sql
CREATE TABLE finance_semmary(
    sector STRING,
    total_value DOUBLE,
    avg_price DOUBLE,
    total_volume BIGINT,
    transaction_count BIGINT
) WITH (
    'connector' = 'filesystem',
    'path' = '{output_dir}',
    'format' = 'csv',
    'csv.field-delimiter' = ','
)
```

*   `finance_summary` 테이블은 SQL 결과가 저장될 출력용 테이블.
    
*   DDL에서 직접 **파일 경로**와 **포맷(csv)** 을 지정함.
    

<br>

### ⑤ SQL 집계 수행 및 결과 출력

```sql
SELECT
    sector,
    SUM(price * volume) as total_value,
    AVG(price) as avg_price,
    SUM(volume) as total_volume,
    COUNT(*) as transaction_count
FROM
    finance
GROUP BY
    sector
```

*   각 섹터별로 거래 요약 통계를 계산:
    
    *   `총 거래액`: 가격 × 수량
        
    *   `평균 가격`: 평균 주가
        
    *   `총 거래량`: 거래 수량 총합
        
    *   `거래 건수`: 해당 섹터에서 발생한 거래 횟수
        

<br>

📌 출력 예시 (콘솔)
-------------

```plaintext
=== 섹터별 금융 데이터 요약 ===
섹터    총 거래액     평균 가격   총 거래량   거래 건수
--------------------------------------------------------------------------------
biotech    211,384,993.26    536,821.33   395,482     326
internet   189,222,123.11    512,006.45   367,111     322
semiconductor  200,144,872.70  504,981.14   380,913     352
```

*   CSV 출력 파일도 동일한 정보를 포함하며, `output_dir` 경로에 저장됨.
    

<br>
<br>

⚙️ 3. 전체 코드 + 상세 주석
===================

```python
# Flink Table API 환경 및 파이썬 기본 모듈 불러오기
from pyflink.table import EnvironmentSettings, TableEnvironment
import tempfile  # 임시 파일/폴더 생성을 위한 모듈
import os
import pandas as pd  # (데이터 검토용 - 실제 실행에는 사용되지 않음)
import numpy as np
import logging

# 로그 설정 (정보 단위 메시지를 출력)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Flink 배치 처리 시작")

    # 1. Flink 환경 설정: 배치 모드로 동작하도록 설정
    env_settings = EnvironmentSettings.in_batch_mode()
    table_env = TableEnvironment.create(env_settings)

    # 병렬 처리 수 설정: 1로 지정하여 출력 파일이 하나로 생성되도록 함
    config = table_env.get_config().get_configuration()
    config.set_string("parallelism.default", "1")

    # 2. 샘플 CSV 데이터 생성
    input_path = create_sample_csv()

    # 3. 결과 저장 디렉토리 설정 및 초기화
    output_dir = tempfile.gettempdir() + '/flink_finance_output'
    if os.path.exists(output_dir):
        import shutil
        shutil.rmtree(output_dir)  # 기존 결과 제거

    # 4. 소스 테이블 정의 (CSV -> Table 매핑)
    source_ddl = f"""
    CREATE TABLE finance(
        stock_code STRING,
        sector STRING,
        price DOUBLE,
        volume INT,
        transaction_date STRING
    ) WITH(
        'connector' = 'filesystem',
        'path' = '{input_path}',
        'format' = 'csv',
        'csv.field-delimiter' = ',',
        'csv.ignore-parse-errors' = 'true'
    )
    """
    table_env.execute_sql(source_ddl)

    # 5. 결과 저장용 싱크 테이블 정의 (Table -> CSV)
    sink_ddl = f"""
    CREATE TABLE finance_semmary(
        sector STRING,
        total_value DOUBLE,
        avg_price DOUBLE,
        total_volume BIGINT,
        transaction_count BIGINT
    ) WITH (
        'connector' = 'filesystem',
        'path' = '{output_dir}',
        'format' = 'csv',
        'csv.field-delimiter' = ','
    )
    """
    table_env.execute_sql(sink_ddl)

    # 6. SQL 집계 쿼리 실행 (섹터별 통계 집계)
    result = table_env.execute_sql("""
    INSERT INTO finance_semmary
    SELECT
        sector,
        SUM(price * volume) as total_value,
        AVG(price) as avg_price,
        SUM(volume) as total_volume,
        COUNT(*) as transaction_count
    FROM
        finance
    GROUP BY
        sector
    """)

    # 7. 결과 출력 (콘솔)
    print("\n=== 섹터별 금융 데이터 요약 ===")
    print("섹터\t총 거래액\t평균 가격\t총 거래량\t거래 건수")
    print("-" * 80)
    with result.collect() as results:
        for row in results:
            print(f"{row[0]}\t{row[1]:,.2f}\t{row[2]:,.2f}\t{row[3]:,}\t{row[4]:,}")

# 샘플 데이터를 생성하고 임시 CSV 파일로 저장하는 함수
def create_sample_csv():
    temp_file = tempfile.gettempdir() + '/finance_data.csv'
    np.random.seed(42)  # 재현 가능성 확보

    # 샘플 주식 코드와 섹터 목록
    stock_codes = ['005930', '000660', '035420', '068270']
    sectors = ['semiconductor', 'biotech', 'internet']

    # 데이터 생성
    data = []
    for _ in range(1000):
        stock_code = np.random.choice(stock_codes)
        sector = np.random.choice(sectors)
        price = round(np.random.uniform(50000, 1000000), 2)
        volume = np.random.randint(10, 1000)
        date = f"2024-{np.random.randint(1, 13):02d}-{np.random.randint(1, 29):02d}"
        data.append(f"{stock_code},{sector},{price},{volume},{date}")

    # CSV 파일로 저장
    with open(temp_file, 'w') as f:
        f.write('\n'.join(data))

    return temp_file

# main 함수 실행
if __name__ == '__main__':
    main()
```

<br>
<br>

📚 4. 추가 설명 및 실무 팁
==================

❗ 실습 시 자주 발생하는 문제와 해결법
----------------------

| 문제 | 원인 | 해결 방안 |
| --- | --- | --- |
| **CSV 파일 인식 오류** | 스키마와 실제 데이터 타입 불일치 | `csv.ignore-parse-errors = true` 사용, 또는 `schema()`에서 타입 명시 |
| **출력 결과가 여러 파일로 나뉨** | 기본 병렬성이 1 이상 | `parallelism.default = 1`로 설정 |
| **`collect()` 호출 시 결과 없음** | `SELECT`만 했고 `INSERT INTO` 누락 | 반드시 `INSERT INTO` sink\_table을 수행해야 파일에 결과가 저장됨 |
| **임시 파일 누락** | `create_sample_csv()` 호출 전 경로 문제 | 파일 경로 확인 또는 `tempfile` 사용 권장 |

<br>

💡 실무에서 어떻게 활용되는가?
------------------

### ✅ 대표 활용 사례

*   **거래소 데이터 분석**: 주식/암호화폐의 가격, 거래량, 섹터별 흐름 분석
    
*   **실시간 리포트 생성**: 매일 밤 또는 시간 단위로 데이터 집계 후 PDF/보고서로 변환
    
*   **대용량 로그 집계**: 서버 로그를 날짜·IP·요청 유형별로 그룹화하여 이상 탐지
    
*   **Flink + Kafka 연계**: Kafka에서 실시간 주식 데이터 수신 → Flink로 처리 → 실시간 DB 저장
    

<br>

🧭 학습 확장 포인트
------------

| 확장 주제 | 설명 |
| --- | --- |
| **Flink Streaming 모드로 전환** | `EnvironmentSettings.in_streaming_mode()`로 변경하여 실시간 흐름 처리 |
| **Kafka 연동** | `connector = 'kafka'` 설정을 통해 실시간 스트림 처리 가능 |
| **Time-based Grouping** | `TUMBLE(transaction_time, INTERVAL '1' HOUR)` 등으로 시간 단위 집계 |
| **Parquet, JSON 포맷** | 결과 포맷을 CSV 외에도 Parquet, JSON 등으로 다양화하여 Spark와 연계 가능 |
| **Flink SQL Gateway** | 코드 없이 SQL만으로 Flink 파이프라인 실행 (운영 환경에 적합) |

<br>

🔍 심화 학습 팁
----------

*   **Table API vs DataStream API**: Table API는 SQL 기반 처리에 강하고, DataStream API는 유연한 사용자 정의 연산에 적합하다.
    
*   **Flink SQL과 Spark SQL 비교 학습**: 배치 처리 시 성능/확장성 차이를 실험해 보면 학습 효과 큼.
    
*   **Kafka-Flink 연동 프로젝트**: 실제 RSS 뉴스나 주가 데이터를 Kafka로 수집하여 Flink로 분석하는 프로젝트 구성 추천.
    

<br>

✅ 마무리 요약
--------

이 실습은 Flink의 배치 환경에서 Table API와 SQL을 통해 파일 기반 데이터를 처리하는 전 과정을 담고 있다.  
실제 데이터 환경에서는 Kafka, Hive, JDBC 등 다양한 소스와 싱크가 함께 쓰이며, 본 예제는 그 구조를 간단한 형태로 축소해 이해를 돕는다.

> 데이터를 "어떻게 저장하고", "어떻게 집계하고", "어디로 전달할지"에 대한 end-to-end 감각을 키우는 것이 Flink 학습의 핵심이다.
