# 금융 데이터를 활용한 기본 데이터 처리

📘 1\. 실습 주제 개요
---------------

이번 실습의 목적은 CSV 파일로부터 로딩한 거래 데이터를 기반으로, PyFlink의 `DataStream API`를 이용해 **거래 유형별 총 금액을 실시간으로 집계**하는 것이다.  
이 실습은 단순한 WordCount에서 나아가, **(key, value) 형식 데이터를 그룹핑하고 누적 합산하는 기본적인 aggregation 구조**를 구현하는 예제다.

### 🔍 실습 흐름 요약

> CSV → (transaction\_type, amount) 추출 → 결측값 제거 → 스트림 생성 → key\_by → reduce → 출력

이 흐름은 실시간 거래 모니터링 시스템, 분류별 로그 집계, 이벤트 유형별 수량 집계 등 실무에서 자주 활용되는 패턴이다.

<br>

### 실습의 주요 학습 목표:

*   Pandas와 PyFlink 간 데이터 흐름 이해
    
*   Flink의 `key_by` 및 `reduce` 연산의 역할 습득
    
*   튜플 기반 스트림 처리 구조 구현
    
*   병렬 환경에서의 스트림 집계 구조 이해
    

<br>
<br>

🛠️ 2\. 코드 구조 및 흐름 해설 + 실행 결과 예시 및 해설
-------------------------------------

### 🔧 1단계: 실행 환경 설정

```python
env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(2)
```

*   Flink의 스트림 실행 환경을 생성
    
*   병렬성을 2로 지정 → 연산자 인스턴스가 2개로 분산 실행됨
    
*   실무에서는 소스, 키 수, task slot 개수에 따라 병렬성 설정을 조정함
    

<br>

### 📄 2단계: Pandas로 CSV 데이터 로딩

```python
df = pd.read_csv("../data/data.csv")
df = df[['transaction_type', 'amount']].dropna()
df['amount'] = df['amount'].astype(int)
transactions = df.values.tolist()
```

*   Pandas로 거래 데이터를 로딩하고, 필요한 두 개의 컬럼만 선택
    
*   결측값 제거 후 `amount` 컬럼은 정수형으로 변환
    
*   `.values.tolist()`로 PyFlink 스트림에 맞게 리스트 형태로 변환
    

예시 입력 데이터:

```python
[
  ["purchase", 100],
  ["refund", 50],
  ["purchase", 150],
  ["transfer", 200]
]
```

<br>

### 🌊 3단계: Flink 스트림 생성

```python
transaction_stream = env.from_collection(
    transactions,
    type_info=Types.TUPLE([Types.STRING(), Types.INT()])
)
```

*   `from_collection()`으로 Python 리스트 데이터를 Flink의 `DataStream`으로 변환
    
*   각 요소는 `(거래 유형: str, 금액: int)` 형식의 튜플
    

<br>

### ➕ 4단계: keyBy + reduce를 통한 집계

```python
transaction_total = (
    transaction_stream
    .key_by(lambda x: x[0])  # 거래 유형별 그룹핑
    .reduce(lambda a, b: (a[0], a[1] + b[1]))  # 금액 누적 합산
)
```

*   `key_by(lambda x: x[0])`: 첫 번째 요소(거래 유형)를 기준으로 데이터를 파티셔닝함
    
*   `reduce(...)`: 같은 키를 가진 레코드들이 들어올 때마다 누적 합산을 수행함
    

예시 흐름:

```
("purchase", 100)
("purchase", 150) → reduce → ("purchase", 250)
```

<br>

### 📤 5단계: 결과 출력 및 실행

```python
transaction_total.print()
env.execute("Transaction Type Aggregation")
```

*   최종 집계된 결과를 콘솔에 출력
    
*   `env.execute(...)`는 반드시 호출되어야 Flink 프로그램이 실제 실행됨
    

<br>

### 🖥️ 실행 결과 예시

입력 CSV:

```csv
transaction_type,amount
purchase,100
refund,50
purchase,150
transfer,200
```

출력 (streaming이므로 순서는 유동적일 수 있음):

```
(purchase, 100)
(refund, 50)
(purchase, 250)
(transfer, 200)
```

<br>
<br>

⚙️ 3\. 전체 코드 + 상세 주석
--------------------

```python
import pandas as pd
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common.typeinfo import Types

def main():
    # Flink의 실행 환경을 설정 (DataStream 처리의 시작점)
    env = StreamExecutionEnvironment.get_execution_environment()

    # 병렬성을 2로 설정 → 연산자 인스턴스가 2개로 병렬 실행됨
    env.set_parallelism(2)

    # CSV 파일 읽기 (Pandas를 사용해 정적 데이터를 로드)
    df = pd.read_csv("../data/data.csv")

    # 필요한 컬럼만 선택하고, 결측값이 있는 행 제거
    df = df[['transaction_type', 'amount']].dropna()

    # amount 컬럼의 타입을 정수형으로 변환 (문자열로 들어올 수 있기 때문)
    df['amount'] = df['amount'].astype(int)

    # DataFrame을 리스트 형태로 변환 (Flink의 from_collection에 넘기기 위함)
    transactions = df.values.tolist()
    # 예: [["purchase", 100], ["refund", 50], ...]

    # Flink 스트림 생성: 각 요소는 (문자열, 정수) 튜플
    transaction_stream = env.from_collection(
        transactions,
        type_info=Types.TUPLE([Types.STRING(), Types.INT()])  # 데이터 타입 지정
    )

    # 거래 유형별 총 거래 금액을 계산하는 파이프라인 구성
    transaction_total = (
        transaction_stream
        # 거래 유형 (첫 번째 필드)을 기준으로 그룹핑
        .key_by(lambda x: x[0])
        # 같은 거래 유형끼리 금액을 누적 합산
        .reduce(lambda a, b: (a[0], a[1] + b[1]))
    )

    # 결과 출력 (Flink 내장 sink)
    transaction_total.print()

    # Flink 실행: DAG 구성 완료 후 실질적인 실행이 시작되는 트리거
    env.execute("Transaction Type Aggregation")

# 이 Python 파일이 직접 실행될 경우 main() 호출
if __name__ == "__main__":
    main()
```

<br>
<br>

📚 4\. 추가 설명 및 실무 팁
-------------------

### ✅ 실무에서의 활용 시나리오

| 적용 사례 | 설명 |
| --- | --- |
| 실시간 거래 금액 모니터링 | 은행/핀테크 서비스에서 결제·송금·환불 등의 거래 유형별 금액 합산 |
| 이벤트 유형별 집계 | 사용자 클릭, 검색, 로그인 등 로그 유형을 구분하여 통계 집계 |
| 제품 유형별 매출 | 이커머스에서 상품 카테고리별 실시간 매출 추적 |
| 트래픽 소스 분석 | 광고 채널별 유입량 합산 및 비교 분석 |

이처럼 `key_by → reduce` 패턴은 **스트리밍 환경에서 실시간 집계를 구현하는 표준 구조**이며, 거의 모든 실무 시스템에서 사용된다.

<br>

### ⚠️ 실무에서 자주 하는 실수

| 실수 | 설명 및 해결책 |
| --- | --- |
| ❌ `amount` 컬럼이 float인데 int로 강제 변환 | 데이터 손실 가능성 있음 → 실제 서비스에서는 `float` 유지 또는 소수점 반올림 필요 |
| ❌ `reduce()` 대신 `map()`으로 합산 시 누적 불가 | `reduce()`는 상태(state)를 유지하면서 누적, `map()`은 stateless |
| ❌ keyBy 대상 필드가 `None`이 포함된 경우 | Flink의 파티셔닝이 실패하거나 job이 crash → 사전 결측값 제거 필수 |
| ❌ 타입 지정 누락 (`type_info`) | PyFlink는 명시적 타입 선언이 필요 → Flink 타입 시스템과 연동됨 |

<br>

### 🔁 실무 확장 방향

#### 1\. **Kafka 연동**

*   거래 데이터가 Kafka 토픽으로 들어오는 경우:
    
    *   Source: KafkaConsumer
        
    *   Sink: KafkaProducer or Database
        

#### 2\. **시간 기반 윈도우 집계로 확장**

*   하루/1시간/5분 단위로 거래 금액을 집계하려면:
    
    ```python
    .key_by(...)
    .window(TumblingProcessingTimeWindows.of(Time.minutes(5)))
    .reduce(...)
    ```
    

#### 3\. **결과 시각화/저장**

*   `.add_sink(...)`를 사용하여 다음 위치로 저장 가능:
    
    *   CSV 파일
        
    *   PostgreSQL
        
    *   Elasticsearch → Kibana 시각화
        
    *   Grafana via Prometheus
        

#### 4\. **PyFlink Table API 전환**

*   동일 집계를 SQL 스타일로 수행 가능:
    
    ```sql
    SELECT transaction_type, SUM(amount)
    FROM transactions
    GROUP BY transaction_type
    ```
    

<br>

### 🧠 병렬성 적용 시 유의사항

| 요소 | 설명 |
| --- | --- |
| `.key_by()` 이후 | 데이터는 해시 파티셔닝되어 병렬 연산자로 분산됨 |
| `.reduce()`는 key 단위 state 유지 | Flink의 managed state를 통해 fault-tolerant 상태 유지 |
| `env.set_parallelism(n)` | 병렬성이 높아질수록 Throughput 증가, 단 결과 순서는 비결정적 |

<br>

### ✅ 마무리 요약

*   이 실습은 PyFlink에서 실시간 집계를 구현하는 가장 핵심적인 패턴인 `key_by → reduce` 구조를 정확히 반영한 실용 예제다.
    
*   실무 확장이 매우 용이하며, Kafka 등 스트리밍 소스를 붙이기만 하면 실시간 분석 시스템으로 전환할 수 있다.
    
*   Flink의 상태 기반 처리(Stateful Processing), 병렬 분산 처리, 데이터 타입 시스템에 대한 감각을 함께 익힐 수 있는 좋은 출발점이다.
    
