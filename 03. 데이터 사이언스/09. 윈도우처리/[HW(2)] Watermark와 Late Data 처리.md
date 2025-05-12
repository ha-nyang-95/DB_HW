# Watermark와 Late Data 처리

📘 1\. 실습 주제 개요
---------------

이번 실습은 Flink 스트림 처리 환경에서 **거래 금액이 특정 임계값(8000)을 초과하는 이상 거래를 실시간으로 감지**하고,  
그 시점의 **워터마크와 함께 이상 거래 정보를 출력**하는 스트리밍 파이프라인을 구현하는 것이다.

이 실습은 다음의 핵심 개념을 포함한다:

*   **WatermarkStrategy**를 이용한 이벤트 시간 기반 스트림 구성
    
*   **TumblingProcessingTimeWindows** 윈도우를 통한 시간 단위 집계
    
*   **ProcessFunction**을 이용해 윈도우 결과에서 조건 기반 이벤트 필터링 수행
    
*   **실시간 모니터링용 이상 거래 탐지 로직 구현**
    

<br>

### 실습 흐름 요약

> CSV 데이터 로드 → 밀리초 단위 타임스탬프 변환  
> → 워터마크 전략 + 타임스탬프 할당  
> → 거래 ID 기준 그룹화 + 10초 간격 윈도우  
> → 거래 금액 누적 → ProcessFunction으로 이상 탐지  
> → 결과 출력

<br>

### 학습 목표

*   이벤트 시간 기반 처리와 프로세싱 시간 기반 윈도우의 차이 이해
    
*   워터마크를 이용한 데이터 지연 허용 방식 습득
    
*   ProcessFunction 내부에서 워터마크를 활용한 고급 조건 처리 방법 익히기
    
*   실시간 이상 탐지 파이프라인의 구조와 구현 흐름 체득
    

<br>
<br>

🛠️ 2\. 코드 구조 및 흐름 해설 + 실행 결과 예시 및 해설
-------------------------------------

### 🧱 1단계: Flink 실행 환경 및 데이터 준비

```python
env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(1)
```

*   Flink 스트림 실행 환경 생성
    
*   병렬성 1 → 이상 거래 탐지 메시지가 순차적으로 출력되도록 구성
    

```python
df = pd.read_csv("../data/data.csv")
transactions = df[['transaction_id', 'timestamp', 'amount']].dropna().values.tolist()
```

*   Pandas를 사용해 거래 데이터 로드 후, 필요한 컬럼만 추출
    

```python
transactions = [(str(t[0]), int(datetime.strptime(t[1], "%Y-%m-%d %H:%M:%S").timestamp() * 1000), float(t[2])) for t in transactions]
```

*   timestamp 문자열을 밀리초 단위 Unix timestamp로 변환
    
*   Flink 이벤트 시간 기준 단위는 **epoch milliseconds**
    

<br>

### 🌊 2단계: Flink 스트림 생성 및 워터마크 전략 설정

```python
source = env.from_collection(
    transactions,
    type_info=Types.TUPLE([Types.STRING(), Types.LONG(), Types.FLOAT()])
)
```

*   Flink `DataStream`으로 변환
    
*   각 요소는 `(transaction_id, timestamp(ms), amount)` 튜플
    

```python
watermark_strategy = (
    WatermarkStrategy.for_bounded_out_of_orderness(Duration.of_seconds(1))
    .with_timestamp_assigner(CustomTimestampAssigner())
)
```

*   최대 1초의 데이터 지연 허용
    
*   `CustomTimestampAssigner`를 통해 두 번째 필드(timestamp)를 이벤트 시간으로 지정
    

```python
watermarked_stream = source.assign_timestamps_and_watermarks(watermark_strategy)
```

*   이벤트 시간 + 워터마크가 할당되어, 지연된 이벤트도 허용 가능
    

<br>

### ⏱️ 3단계: 윈도우 집계 (Processing Time 기반)

```python
windowed_stream = (
    watermarked_stream
    .key_by(lambda x: x[0])  # 거래 ID 기준 그룹핑
    .window(TumblingProcessingTimeWindows.of(Time.seconds(10)))  # 프로세싱 시간 기준 10초 윈도우
    .reduce(lambda a, b: (a[0], a[1], a[2] + b[2]))  # 거래 금액 누적 합산
)
```

*   주의: **TumblingProcessingTimeWindows**는 이벤트 시간이 아닌 **Flink 처리 시점** 기준으로 동작
    
*   각 윈도우 내에서 같은 거래 ID끼리 금액을 누적하여 하나의 튜플로 압축됨
    

<br>

### 🔍 4단계: 이상 거래 감지 로직 (ProcessFunction)

```python
class AnomalyDetectionProcess(ProcessFunction):
    def process_element(self, value, ctx):
        watermark = ctx.timer_service().current_watermark()
        if value[2] > 8000:
            print(f"이상 거래 감지: {value}, 현재 워터마크: {watermark}")
        yield value
```

*   Reduce된 결과가 이 함수로 전달됨
    
*   거래 금액이 8000을 초과하면 **이상 거래로 감지**하고, 워터마크와 함께 콘솔에 출력
    
*   `ctx.timer_service().current_watermark()`를 통해 **현재 워터마크** 조회 가능
    

```python
anomaly_stream = windowed_stream.process(AnomalyDetectionProcess())
```

*   감지 로직 적용
    

<br>

### 📤 5단계: 출력 및 실행

```python
anomaly_stream.print("Anomaly Detection")
env.execute("Transaction Anomaly Detection")
```

*   감지된 거래 데이터를 콘솔에 출력
    
*   Flink 스트리밍 잡 실행
    

<br>

### 🖥️ 실행 결과 예시

입력 예시:

```csv
transaction_id,timestamp,amount
tx1,2024-05-11 10:00:00,3200
tx1,2024-05-11 10:00:05,6000
tx1,2024-05-11 10:00:09,2500
tx1,2024-05-11 10:00:10,9000
```

출력 예시 (윈도우 단위 Reduce → 이상 감지):

```
이상 거래 감지: ('tx1', 1715392810000, 9000.0), 현재 워터마크: 1715392809000
Anomaly Detection> ('tx1', 1715392810000, 9000.0)
```

*   마지막 거래 금액(9000.0)이 조건을 초과하여 이상 거래로 감지됨
    
*   워터마크는 해당 시점 기준의 마지막 도달 시간
    

<br>
<br>

⚙️ 3\. 전체 코드 + 상세 주석
--------------------

```python
import pandas as pd
from datetime import datetime

# Flink API 관련 모듈
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common.watermark_strategy import WatermarkStrategy, TimestampAssigner
from pyflink.datastream.window import TumblingProcessingTimeWindows  # 윈도우 타입
from pyflink.common import Duration, Time
from pyflink.common.typeinfo import Types
from pyflink.datastream.functions import ProcessFunction

# ✅ 사용자 정의 타임스탬프 추출기
class CustomTimestampAssigner(TimestampAssigner):
    def extract_timestamp(self, element, record_timestamp):
        # 데이터의 두 번째 필드(Unix timestamp in ms)를 이벤트 시간으로 사용
        return element[1]

# ✅ 이상 거래 감지용 ProcessFunction 정의
class AnomalyDetectionProcess(ProcessFunction):
    def process_element(self, value, ctx):
        # 현재 워터마크(지연 허용 기준 시간)를 가져옴
        watermark = ctx.timer_service().current_watermark()

        # 거래 금액이 8000을 초과하는 경우 이상 거래로 판단
        if value[2] > 8000:
            print(f"이상 거래 감지: {value}, 현재 워터마크: {watermark}")

        # 그대로 결과를 출력으로 내보냄
        yield value

def main():
    # ✅ Flink 스트리밍 환경 생성
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)  # 단일 스레드로 실행하여 출력 순서 확인 용이

    # ✅ CSV 파일 로드 및 필드 정제
    df = pd.read_csv("../data/data.csv")
    transactions = df[['transaction_id', 'timestamp', 'amount']].dropna().values.tolist()

    # ✅ timestamp 문자열을 밀리초 단위 Unix 시간으로 변환
    transactions = [
        (str(t[0]), int(datetime.strptime(t[1], "%Y-%m-%d %H:%M:%S").timestamp() * 1000), float(t[2]))
        for t in transactions
    ]

    # ✅ Flink 스트림 생성 (transaction_id, timestamp(ms), amount)
    source = env.from_collection(
        transactions,
        type_info=Types.TUPLE([Types.STRING(), Types.LONG(), Types.FLOAT()])
    )

    # ✅ 워터마크 전략: 최대 1초 지연 허용
    watermark_strategy = (
        WatermarkStrategy.for_bounded_out_of_orderness(Duration.of_seconds(1))
        .with_timestamp_assigner(CustomTimestampAssigner())  # 사용자 정의 TimestampAssigner 사용
    )

    # ✅ 워터마크 및 타임스탬프 할당
    watermarked_stream = source.assign_timestamps_and_watermarks(watermark_strategy)

    # ✅ 프로세싱 시간 기반 텀블링 윈도우 (10초 단위)
    windowed_stream = (
        watermarked_stream
        .key_by(lambda x: x[0])  # 거래 ID로 그룹화
        .window(TumblingProcessingTimeWindows.of(Time.seconds(10)))  # 프로세싱 시간 기준 10초 윈도우
        .reduce(lambda a, b: (a[0], a[1], a[2] + b[2]))  # 금액 합산
    )

    # ✅ 이상 거래 감지 프로세스 적용
    anomaly_stream = windowed_stream.process(AnomalyDetectionProcess())

    # ✅ 결과 출력
    anomaly_stream.print("Anomaly Detection")

    # ✅ 잡 실행
    env.execute("Transaction Anomaly Detection")

# ✅ 메인 함수 실행
if __name__ == "__main__":
    main()
```

<br>
<br>

📚 4\. 추가 설명 및 실무 팁
-------------------

### ✅ 이벤트 시간 vs 프로세싱 시간

| 기준 | 이벤트 시간 (Event Time) | 프로세싱 시간 (Processing Time) |
| --- | --- | --- |
| 기준 시점 | 데이터 발생 시점 | Flink가 데이터를 처리한 시점 |
| 워터마크 사용 | 필요 (Watermark 필수) | 필요 없음 |
| 실시간성 | 데이터 순서 보장 필요 | 순서 무관, 빠른 처리 |
| 실무 용도 | 정확한 집계, 지연 허용 (로그, 거래 분석) | 빠른 반응성 (알람, UI 등) |

> 이 실습에서는 **이벤트 시간으로 워터마크를 설정**,  
> **프로세싱 시간 기반 윈도우**를 사용하여 **지연 허용 + 빠른 집계 반응성**을 동시에 테스트했어.

<br>

### 🧠 ProcessFunction 실무 사용 예

| 사용 목적 | 활용 방식 |
| --- | --- |
| 이상 탐지 | `if 조건:` 판단 후 `print()` 또는 `SideOutput`으로 알림 |
| 워터마크 추적 | `ctx.timer_service().current_watermark()` 사용 |
| 알람 트리거 | 타이머(`ctx.timer_service().register_event_time_timer`)로 특정 조건 도달 시 알림 |
| 외부 API 연동 | `process_element` 내부에서 REST API 호출 가능 (비권장, 성능 저하 우려) |

<br>

### ⚠️ 실무에서 자주 발생하는 실수

| 실수 | 설명 |
| --- | --- |
| ❌ 이벤트 시간 기반 윈도우인데 워터마크를 설정하지 않음 | 집계가 끝나지 않음 (무한 대기) |
| ❌ 이벤트 시간 기반인데 프로세싱 윈도우 사용 | 집계 기준이 엉킬 수 있음 (지연 데이터 누락) |
| ❌ ProcessFunction에서 `yield` 누락 | 결과 출력이 안 됨 |
| ❌ 타임스탬프 밀리초 변환 누락 | Flink가 인식 못함 → 집계 실패 |

<br>

### 🔧 실무 확장 전략

#### ✅ 1\. 이상 거래 메시지 Kafka로 전송

```python
# ProcessFunction 내부에서 이상 거래만 Kafka sink로 출력
```

#### ✅ 2\. 타이머 등록 + 시간 기반 경고

```python
# 일정 시간 동안 거래가 없으면 알림
ctx.timer_service().register_event_time_timer(...)
```

#### ✅ 3\. SideOutput을 사용해 이상 거래만 분리 출력

```python
self.output(self.output_tag, value)
```

#### ✅ 4\. 지표 기반 탐지 로직으로 확장

*   평균, 편차, 상한선 계산 → 이상 판단
    
*   ML 모델 결과값과 연계하여 이상 판단
    

<br>

### ✅ 마무리 요약

*   이 실습은 Flink에서 이벤트 시간 기반 워터마크와 프로세싱 시간 윈도우를 혼합하여,  
    실시간 반응성과 지연 허용성을 모두 고려한 파이프라인을 구성한 예제이다.
    
*   ProcessFunction은 고급 제어 흐름, 이상 탐지, 사용자 정의 알림 처리 등에 유용하게 쓰인다.
    
*   실무에서는 SideOutput, Kafka sink, 타이머, 알람 시스템과의 연동 등으로 이 구조를 확장해 나가야 한다.
    
