# Tumbling 윈도우를 활용한 금융 데이터 평균 계산

📘 1\. 실습 주제 개요
---------------

이번 실습의 목적은 PyFlink에서 **거래 데이터를 이벤트 시간(event time)** 기준으로 5초 단위로 나누고,  
각 구간에 대해 거래 금액(`amount`)의 평균을 **사용자 정의 집계 함수(AggregateFunction)** 로 계산하는 것이다.

실습에는 다음의 핵심 개념들이 모두 포함된다:

*   **이벤트 시간 처리 (Event Time Processing)**
    
*   **워터마크 (Watermark)** 설정을 통한 지연 데이터 처리 허용
    
*   **Tumbling Event Time Window**: 고정 시간 간격의 집계 단위
    
*   **사용자 정의 집계 함수 (UDAF)**: 평균을 직접 누적하여 계산
    
<br>

### 실습 흐름 요약

> Pandas CSV → 거래 ID, timestamp, 금액 추출  
> → 밀리초 단위 timestamp 변환 → Flink Stream 생성  
> → Timestamp Assigner + Watermark 설정  
> → KeyBy + TumblingEventTimeWindow + AggregateFunction  
> → 평균 결과 출력

<br>

### 학습 목표

*   이벤트 시간 기반의 윈도우 집계 구성법 이해
    
*   `.assign_timestamps_and_watermarks()` 사용법 습득
    
*   Tumbling 윈도우의 동작 방식 파악
    
*   사용자 정의 AggregateFunction 구현 및 활용 방법 익히기
    
*   실시간 평균 계산 흐름을 체계적으로 구성하는 능력 확보
    

<br>
<br>

🛠️ 2\. 코드 구조 및 흐름 해설 + 실행 결과 예시 및 해설
-------------------------------------

### 🔧 1단계: 실행 환경 및 데이터 로딩

```python
env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(2)
```

*   Flink 실행 환경 초기화
    
*   병렬성 2로 설정 → 데이터가 병렬 처리될 수 있도록 설정
    

```python
df = pd.read_csv("../data/data.csv")
transactions = df[['transaction_id', 'timestamp', 'amount']].dropna().values.tolist()
```

*   Pandas를 통해 거래 데이터를 불러오고, 필요한 컬럼만 추출
    
*   결측값 제거
    

<br>

### ⏱️ 2단계: 이벤트 시간 추출 및 밀리초 변환

```python
transactions = [
    (str(t[0]), int(datetime.strptime(t[1], "%Y-%m-%d %H:%M:%S").timestamp() * 1000), float(t[2]))
    for t in transactions
]
```

*   `timestamp` 문자열을 `datetime`으로 파싱 후 **Unix timestamp(초) × 1000 → 밀리초**로 변환
    
*   Flink의 이벤트 시간 처리 기준 단위는 **epoch milliseconds**
    

<br>

### 🌊 3단계: 데이터 스트림 생성

```python
source = env.from_collection(
    transactions,
    type_info=Types.TUPLE([Types.STRING(), Types.LONG(), Types.FLOAT()])
)
```

*   Flink의 `DataStream`으로 변환
    
*   각 요소는 `(transaction_id, timestamp, amount)` 형식의 튜플
    

<br>

### 💧 4단계: 워터마크 전략 및 타임스탬프 할당

```python
class CustomTimestampAssigner(TimestampAssigner):
    def extract_timestamp(self, element, record_timestamp):
        return element[1]
```

*   사용자 정의 `TimestampAssigner`
    
*   이벤트의 두 번째 필드(밀리초 timestamp)를 이벤트 시간으로 사용
    

```python
watermark_strategy = (
    WatermarkStrategy.for_bounded_out_of_orderness(Duration.of_seconds(1))
    .with_timestamp_assigner(CustomTimestampAssigner())
)
```

*   **bounded out-of-orderness**: 최대 1초까지 지연된 이벤트 허용
    
*   워터마크는 이벤트 시간의 진행을 나타내며, 윈도우 트리거의 기준이 됨
    

```python
watermarked_stream = source.assign_timestamps_and_watermarks(watermark_strategy)
```

*   각 요소에 이벤트 시간 및 워터마크를 할당하여 **정확한 시간 기반 처리** 가능하게 함
    

<br>

### 🧩 5단계: Tumbling 윈도우 집계

```python
class AverageAggregate(AggregateFunction):
    def create_accumulator(self):
        return (0.0, 0)

    def add(self, value, accumulator):
        return (accumulator[0] + value[2], accumulator[1] + 1)

    def get_result(self, accumulator):
        return accumulator[0] / accumulator[1] if accumulator[1] > 0 else 0

    def merge(self, acc1, acc2):
        return (acc1[0] + acc2[0], acc1[1] + acc2[1])
```

*   사용자 정의 집계 함수 (UDAF)
    
*   합계와 개수를 누적하고, 최종적으로 평균 계산
    

```python
avg_window_stream = (
    watermarked_stream
    .key_by(lambda x: x[0])  # transaction_id를 기준으로 그룹핑
    .window(TumblingEventTimeWindows.of(Time.seconds(5)))  # 5초 간격의 고정 윈도우
    .aggregate(AverageAggregate())  # 평균 집계
)
```

*   고정 길이(5초)의 이벤트 시간 기반 윈도우 생성
    
*   각 윈도우마다 집계 함수 호출 → 평균 거래 금액 계산
    

<br>

### 📤 6단계: 출력 및 실행

```python
avg_window_stream.print("Tumbling Window Avg")
env.execute("Tumbling Window Average Calculation")
```

*   윈도우 별 평균 결과를 콘솔에 출력
    
*   Flink 스트리밍 잡 실행
    

<br>

### 🖥️ 실행 결과 예시

입력 예:

```csv
transaction_id,timestamp,amount
tx1,2024-05-11 10:00:00,100
tx1,2024-05-11 10:00:03,200
tx1,2024-05-11 10:00:06,300
```

출력 예 (윈도우별 평균):

```
Tumbling Window Avg: 150.0   # 윈도우: 10:00:00 ~ 10:00:05
Tumbling Window Avg: 300.0   # 윈도우: 10:00:05 ~ 10:00:10
```

*   이벤트 시간 기준으로 윈도우가 정해지고, 각 윈도우 내의 금액 평균이 계산됨
    

<br>
<br>

⚙️ 3\. 전체 코드 + 상세 주석
--------------------

```python
import pandas as pd
from datetime import datetime

# Flink 실행 및 스트림 구성 관련 모듈
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common.watermark_strategy import WatermarkStrategy, TimestampAssigner
from pyflink.datastream.window import TumblingEventTimeWindows
from pyflink.common import Duration, Time
from pyflink.common.typeinfo import Types
from pyflink.datastream.functions import AggregateFunction


# ✅ 사용자 정의 TimestampAssigner 클래스: 이벤트 시간 추출 로직 정의
class CustomTimestampAssigner(TimestampAssigner):
    def extract_timestamp(self, element, record_timestamp):
        # element[1]: 두 번째 필드인 밀리초 단위 timestamp
        return element[1]


# ✅ 사용자 정의 집계 함수: 거래 금액 평균을 계산하는 AggregateFunction
class AverageAggregate(AggregateFunction):
    def create_accumulator(self):
        # 초기 누적 상태는 (총합, 개수)
        return (0.0, 0)

    def add(self, value, accumulator):
        # amount 필드(value[2])를 합산하고 개수 1 증가
        return (accumulator[0] + value[2], accumulator[1] + 1)

    def get_result(self, accumulator):
        # 평균 계산: 총합 / 개수
        return accumulator[0] / accumulator[1] if accumulator[1] > 0 else 0

    def merge(self, acc1, acc2):
        # 병렬 처리된 부분 결과를 병합 (합계와 개수 합산)
        return (acc1[0] + acc2[0], acc1[1] + acc2[1])


def main():
    # ✅ Flink 실행 환경 설정
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(2)  # 병렬 처리 개수 설정

    # ✅ CSV 파일 로딩 (Pandas 사용)
    df = pd.read_csv("../data/data.csv")

    # ✅ 필요한 컬럼만 추출하고 결측값 제거
    transactions = df[['transaction_id', 'timestamp', 'amount']].dropna().values.tolist()

    # ✅ timestamp 문자열을 밀리초 단위 Unix 시간으로 변환
    transactions = [
        (str(t[0]), int(datetime.strptime(t[1], "%Y-%m-%d %H:%M:%S").timestamp() * 1000), float(t[2]))
        for t in transactions
    ]

    # ✅ Flink 데이터 스트림 생성
    source = env.from_collection(
        transactions,
        type_info=Types.TUPLE([Types.STRING(), Types.LONG(), Types.FLOAT()])
    )

    # ✅ 워터마크 전략 설정: 최대 1초 지연 허용
    watermark_strategy = (
        WatermarkStrategy.for_bounded_out_of_orderness(Duration.of_seconds(1))
        .with_timestamp_assigner(CustomTimestampAssigner())  # 사용자 정의 TimestampAssigner 사용
    )

    # ✅ 워터마크 및 타임스탬프 할당 적용
    watermarked_stream = source.assign_timestamps_and_watermarks(watermark_strategy)

    # ✅ 5초 이벤트 시간 기반 Tumbling 윈도우로 평균 집계
    avg_window_stream = (
        watermarked_stream
        .key_by(lambda x: x[0])  # 거래 ID 기준으로 그룹핑
        .window(TumblingEventTimeWindows.of(Time.seconds(5)))  # 5초 간격 윈도우 설정
        .aggregate(AverageAggregate())  # 사용자 정의 평균 계산 집계 함수 적용
    )

    # ✅ 결과 출력 (윈도우마다 평균 결과 출력됨)
    avg_window_stream.print("Tumbling Window Avg")

    # ✅ Flink Job 실행
    env.execute("Tumbling Window Average Calculation")


# ✅ 실행 트리거
if __name__ == "__main__":
    main()
```

<br>
<br>

📚 4\. 추가 설명 및 실무 팁
-------------------

### ✅ 이벤트 시간 기반 처리의 필요성

| 기준 | 설명 |
| --- | --- |
| 처리 시간 (Processing Time) | 데이터를 실제로 Flink가 처리한 시점 |
| 이벤트 시간 (Event Time) | 데이터가 생성된 실제 시점 (로그 타임스탬프 등) |
| 워터마크 (Watermark) | Flink가 어느 시점까지 데이터를 수신했다고 간주할지 판단하는 기준선 |

> 실무에서는 데이터가 지연 도착하거나 순서가 어긋나는 경우가 많기 때문에,  
> **정확한 집계를 위해서는 Event Time + 워터마크 기반 처리**가 필수야.

<br>

### 🔧 워터마크 전략 실무 예시

```python
WatermarkStrategy
  .for_bounded_out_of_orderness(Duration.of_seconds(3))
  .with_timestamp_assigner(...)
```

*   실시간 로그 데이터 수집 시 2~5초 정도의 지연 허용 설정이 일반적
    
*   너무 짧으면 유실, 너무 길면 처리 지연 발생 → 실측 기반 조정 권장
    

<br>

### 🧠 자주 하는 실수 및 해결법

| 실수 | 설명 및 해결책 |
| --- | --- |
| ❌ timestamp가 `str` 형식 | 반드시 epoch milliseconds (`long`)로 변환해야 함 |
| ❌ 워터마크 설정 누락 | 윈도우 트리거가 무기한 대기 상태에 빠짐 |
| ❌ 타임존 고려 부족 | Flink는 기본적으로 UTC 사용 → `datetime.strptime` 변환 시 로컬 시간대 확인 |
| ❌ get\_result()에서 0으로 나누기 발생 | `accumulator[1] == 0`인 경우 분모 방지 조건 필수 |

<br>

### 🧩 실무 확장 전략

#### ✅ 1\. 슬라이딩 윈도우(SlidingEventTimeWindows)

*   매 5초마다 10초간 평균 계산:
    

```python
.window(SlidingEventTimeWindows.of(Time.seconds(10), Time.seconds(5)))
```

#### ✅ 2\. 세션 윈도우(SessionWindows)

*   간격이 일정 시간 이상 떨어지면 새로운 윈도우 시작:
    

```python
.window(EventTimeSessionWindows.with_gap(Time.minutes(1)))
```

#### ✅ 3\. Table API로 전환

*   SQL 문법으로 윈도우 평균 집계 가능:
    

```sql
SELECT transaction_id, TUMBLE_START(rowtime, INTERVAL '5' SECOND), AVG(amount)
FROM transactions
GROUP BY transaction_id, TUMBLE(rowtime, INTERVAL '5' SECOND)
```

#### ✅ 4\. 이상 감지로 확장

*   평균이 일정 임계치를 초과하면 알림 전송 → SideOutput 또는 Kafka sink 사용
    

<br>

### ✅ 마무리 요약

*   이 실습은 Flink의 이벤트 시간 기반 스트림 처리의 핵심 구조를 다룬다.
    
*   `assign_timestamps_and_watermarks()` → `TumblingEventTimeWindow` → `AggregateFunction` 순의 연산 흐름은 실무 분석 시스템의 기초 구조로 매우 중요하다.
    
*   실시간 통계, 감지, 예측 등 거의 모든 고급 분석은 이 구조를 기반으로 확장된다.
    
