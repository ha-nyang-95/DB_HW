# 실습 정리본 작성 요청

**User:** 장철환(하냥) (wkdcjfghks1@gmail.com)  
**Created:** 5/11/2025 11:48  
**Updated:** 5/11/2025 12:27  
**Exported:** 5/11/2025 12:32  

## Response:
좋아, 이번 실습은 PyFlink 스트림에서 이상 거래(Anomaly)를 실시간으로 탐지하고, 그 결과를 콘솔과 파일로 동시 출력하는 **이상 거래 감지 + 파일 저장** 실습이야.  
지금까지와 동일한 형식으로 다음과 같이 구성된 전문 정리본을 제공할게:

* * *

### ✅ 구성 방식

1.  📘 실습 주제 개요
    
2.  🛠️ 코드 구조 및 흐름 해설 + 실행 결과 예시 및 해설
    
3.  ⚙️ 전체 코드 + 상세 주석
    
4.  📚 추가 설명 및 실무 팁
    

* * *

먼저 시작은 다음과 같아:

* * *

📘 1\. 실습 주제 개요
---------------

이번 실습은 거래 데이터에서 금액(`amount`)이 특정 임계값을 초과하는 이상 거래(Anomaly)를 필터링하여,  
실시간으로 탐지하고 탐지된 결과를 **콘솔 출력 + 파일 저장** 두 방식으로 동시에 출력하는 **Flink 기반 이상 거래 탐지 스트림 처리**이다.

이 실습은 실무에서 다음과 같은 문제를 해결하는 데 적용될 수 있다:

*   금융 이상 거래 탐지 시스템
    
*   고액 전자상거래 결제 추적
    
*   보험 청구 이상 탐지
    
*   규제 위반 거래 로그 분리
    

### 실습 흐름 요약

> Pandas → Flink Stream → 금액 기준 필터링 → 문자열 변환 → 콘솔 출력 + 파일 저장(FileSink)

* * *

### 학습 목표

*   PyFlink에서 `filter()`를 사용한 조건 기반 이상값 탐지 방식 이해
    
*   Java 기반 FileSink 사용법 숙지 (`SimpleStringEncoder` → `Encoder`)
    
*   Flink Stream에서 출력(Sink)을 동시에 여러 개 구성하는 방식 습득
    
*   Pandas + PyFlink 연계 워크플로우의 확장성 체득
    

* * *

이제 다음 메시지에서는 **2\. 코드 구조 및 흐름 해설 + 실행 결과 예시 및 해설**을 아주 상세하게 설명해줄게.  
바로 이어서 진행할게.

## Response:
좋아, 이제 **2\. 코드 구조 및 흐름 해설 + 실행 결과 예시 및 해설**을 단계별로 상세하게 설명할게.  
이번 실습은 PyFlink의 `filter()` + `map()`을 활용하여 이상 거래를 탐지하고, 그 결과를 콘솔과 파일로 동시에 출력하는 방식이야.

* * *

🛠️ 2\. 코드 구조 및 흐름 해설 + 실행 결과 예시 및 해설
-------------------------------------

* * *

### 🔧 1단계: 실행 환경 구성

```python
env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(1)
```

*   Flink 스트림 실행 환경 생성
    
*   병렬성(parallelism)을 1로 설정하여 처리 순서를 직관적으로 확인 가능하도록 함
    

* * *

### 📄 2단계: Pandas로 CSV 데이터 로딩 및 전처리

```python
df = pd.read_csv("../data/data.csv")
transactions = df[["transaction_id", "customer_id", "amount"]].dropna().values.tolist()
```

*   거래 CSV 파일을 Pandas로 로드
    
*   `transaction_id`, `customer_id`, `amount` 컬럼만 사용
    
*   결측값 제거 후 리스트 형태로 변환하여 Flink에 넘김
    

예시 입력:

```python
[
  ["tx1001", "cust1", 7500.0],
  ["tx1002", "cust2", 9200.0],
  ["tx1003", "cust3", 15000.0]
]
```

* * *

### 🌊 3단계: Flink 스트림 생성

```python
transaction_stream = env.from_collection(
    transactions,
    type_info=Types.TUPLE([Types.STRING(), Types.STRING(), Types.FLOAT()])
)
```

*   리스트를 Flink의 `DataStream`으로 변환
    
*   각 요소는 `(거래 ID, 고객 ID, 거래 금액)` 형식의 튜플
    

* * *

### 🚨 4단계: 이상 거래 감지 (Threshold 초과 필터링)

```python
suspicious_transactions = transaction_stream.filter(lambda x: x[2] > THRESHOLD)
```

*   세 번째 필드(`amount`)가 설정된 임계값(8000.0)을 초과하는 데이터만 필터링
    
*   즉, 이상 거래만 추출
    

예시 결과:

```
["tx1002", "cust2", 9200.0]
["tx1003", "cust3", 15000.0]
```

* * *

### 🔄 5단계: 문자열 변환 (파일 저장을 위한 전처리)

```python
formatted_stream = suspicious_transactions.map(
    lambda x: f"{x[0]}, {x[1]}, {x[2]}", 
    output_type=Types.STRING()
)
```

*   튜플 데이터를 문자열로 포맷팅하여 저장 준비
    
*   예: `("tx1002", "cust2", 9200.0)` → `"tx1002, cust2, 9200.0"`
    

* * *

### 🖥️ 6단계: 콘솔 출력

```python
formatted_stream.print()
```

*   실시간 스트림 데이터를 터미널에서 직접 확인
    

* * *

### 📁 7단계: FileSink 설정 및 연결

```python
gateway = get_gateway()
j_string_encoder = gateway.jvm.org.apache.flink.api.common.serialization.SimpleStringEncoder()
encoder = Encoder(j_string_encoder)

file_sink = FileSink.for_row_format("./output/suspicious_transactions", encoder).build()
formatted_stream.sink_to(file_sink)
```

*   Flink에서 파일로 데이터를 저장하려면 Java 엔진(`SimpleStringEncoder`)을 사용해야 함
    
*   `FileSink.for_row_format()`을 통해 Row 단위로 파일 쓰기 구성
    
*   출력 파일은 `./output/suspicious_transactions/` 아래에 저장됨
    

* * *

### ▶️ 8단계: Flink 실행 트리거

```python
env.execute("Anomaly Detection in Transactions with File Sink")
```

*   DAG 실행 트리거. Flink는 `execute()`가 호출되어야 모든 연산이 실제로 시작됨
    

* * *

### 🖥️ 실행 결과 예시

#### 콘솔 출력:

```
tx1002, cust2, 9200.0
tx1003, cust3, 15000.0
```

#### 저장된 파일 (예: `part-0-0`):

```csv
tx1002, cust2, 9200.0
tx1003, cust3, 15000.0
```

> 주의: Flink는 파일 Sink를 사용할 경우, 디렉터리 안에 여러 파일(part-0-0, part-1-0 등)을 나눠 저장할 수 있음

* * *

이제 다음 메시지에서는 **⚙️ 3\. 전체 코드 + 상세 주석**을 제공할게.  
한 줄도 생략하지 않고 모든 코드 줄마다 상세한 설명을 포함할게. 바로 이어서 진행할게.

## Response:
좋아, 이제 이번 실습의 **⚙️ 3\. 전체 코드 + 상세 주석**을 정리해줄게.  
이 코드는 PyFlink로 실시간 이상 거래 탐지를 수행하고, 그 결과를 파일로 저장하는 구조를 완전히 담고 있어.  
모든 구문에 실무 수준의 상세한 설명을 포함했어.

* * *

⚙️ 3\. 전체 코드 + 상세 주석
--------------------

```python
import pandas as pd
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common.typeinfo import Types
from pyflink.datastream.connectors import FileSink
from pyflink.common.serialization import Encoder
from pyflink.java_gateway import get_gateway

# 이상 거래 감지 임계값 설정 (8,000원을 초과하면 이상 거래로 간주)
THRESHOLD = 8000.0

def main():
    # Flink 스트리밍 실행 환경 생성
    env = StreamExecutionEnvironment.get_execution_environment()

    # 병렬성을 1로 설정 (출력 순서를 직관적으로 확인하기 위해 단일 쓰레드 처리)
    env.set_parallelism(1)

    # Pandas를 통해 CSV 파일 로딩
    df = pd.read_csv("../data/data.csv")

    # 필요한 컬럼만 추출하고, 결측값 제거 후 리스트 형태로 변환
    transactions = df[["transaction_id", "customer_id", "amount"]].dropna().values.tolist()
    # 예: [["tx1001", "cust1", 7500.0], ["tx1002", "cust2", 9200.0], ...]

    # Flink DataStream 생성
    # 각 요소는 (문자열, 문자열, 실수형) 튜플로 구성
    transaction_stream = env.from_collection(
        transactions,
        type_info=Types.TUPLE([Types.STRING(), Types.STRING(), Types.FLOAT()])
    )

    # 이상 거래 탐지: 거래 금액이 THRESHOLD를 초과하는 거래만 필터링
    suspicious_transactions = transaction_stream.filter(
        lambda x: x[2] > THRESHOLD  # x[2]는 amount
    )

    # 이상 거래 데이터를 CSV 형태 문자열로 포맷팅
    formatted_stream = suspicious_transactions.map(
        lambda x: f"{x[0]}, {x[1]}, {x[2]}",
        output_type=Types.STRING()
    )

    # 실시간 콘솔 출력 (debugging/logging 용도)
    formatted_stream.print()

    # FileSink 설정: 파일로 출력하기 위한 Java Encoder 구성
    gateway = get_gateway()
    j_string_encoder = gateway.jvm.org.apache.flink.api.common.serialization.SimpleStringEncoder()
    encoder = Encoder(j_string_encoder)

    # FileSink 구성 (디렉토리 경로, 인코더 방식 지정)
    file_sink = FileSink.for_row_format(
        "./output/suspicious_transactions",  # 출력 디렉토리
        encoder
    ).build()

    # Sink에 연결하여 데이터를 파일로 저장
    formatted_stream.sink_to(file_sink)

    # Flink 실행 트리거: 모든 연산 DAG 실행 시작
    env.execute("Anomaly Detection in Transactions with File Sink")

# 메인 함수 실행 트리거
if __name__ == "__main__":
    main()
```

* * *

이 코드는 단순히 이상값을 탐지하고 출력하는 데 그치지 않고, **Java 기반 파일 저장 구조**까지 구현함으로써  
PyFlink에서 실무 수준으로 출력을 다루는 방법을 명확하게 보여줘.

다음 메시지에서는 마지막으로 **📚 4\. 추가 설명 및 실무 팁**을 정리할게.  
실무 확장 방향, 자주 하는 실수, 연동 전략까지 포함해서 마무리하자. 바로 이어서 진행할게.

## Response:
좋아, 이제 마지막 항목인 **📚 4\. 추가 설명 및 실무 팁**을 정리해줄게.  
이번 실습은 PyFlink의 `filter()` 기반 이상 거래 탐지에 Java 기반 `FileSink`를 결합하여,  
**실시간 탐지 + 영속적 저장**이라는 두 가지 목적을 동시에 달성하는 실무 친화적 구성이라고 할 수 있어.

* * *

📚 4\. 추가 설명 및 실무 팁
-------------------

* * *

### ✅ 실무에서의 응용 예시

| 적용 분야 | 설명 |
| --- | --- |
| 금융 거래 모니터링 | 고액 출금·입금, 불규칙한 거래 빈도 탐지 |
| 보험·의료 시스템 | 비정상적으로 높은 청구 금액 선별 |
| 온라인 쇼핑몰 | 자동화된 고액 구매 감지 및 수기 확인 필요 대상 필터링 |
| 로그 이상 탐지 | 응답 시간, 요청 크기, 트래픽 이상치 탐지 |

이처럼 간단한 조건 필터링과 로그 저장의 결합은 \*\*운영 시스템의 관찰성(observability)\*\*과 **데이터 유실 방지**에 있어 매우 유용한 기법이야.

* * *

### ⚠️ 실무에서 자주 발생하는 실수

| 실수 | 설명 및 해결책 |
| --- | --- |
| ❌ 필드 순서 착오 | `x[2] > THRESHOLD`에서 인덱스 오류 → 튜플 구조를 정확히 확인해야 |
| ❌ 문자열 포맷에서 콤마 누락/중복 | 파일 저장 시 CSV 포맷 불일치 → `f"{x[0]}, {x[1]}, {x[2]}"` 명확히 확인 필요 |
| ❌ `SimpleStringEncoder` 사용 누락 | FileSink에서 반드시 Java 기반 Encoder를 연결해야 저장 가능 |
| ❌ 병렬성 설정 무시 | FileSink 사용 시 병렬성에 따라 여러 파일(part-000-0 등)로 저장됨 |
| ❌ Flink 작업 종료 시 파일 write가 반영되지 않음 | 반드시 `env.execute(...)` 호출해야 파일 생성 완료됨 |

* * *

### 🧠 실무 확장 전략

#### 1\. **윈도우 기반 이상 탐지로 확장**

*   단순 임계값을 넘는 것뿐만 아니라, 시간 기반 이상 여부 판단 가능:
    

```python
from pyflink.datastream.window import TumblingProcessingTimeWindows
from pyflink.common.time import Time

stream \
  .key_by(lambda x: x[1]) \
  .window(TumblingProcessingTimeWindows.of(Time.minutes(10))) \
  .reduce(...)
```

#### 2\. **Kafka 연동**

*   Source: Kafka → Flink
    
*   Sink: Kafka or Elasticsearch
    
    이상 탐지된 이벤트만 `alert-topic`으로 publish
    

#### 3\. **Elasticsearch 연동 + Kibana 시각화**

*   파일 출력 대신 `.add_sink(ElasticsearchSink)`으로 전환 가능
    
*   Kibana에서 이상 거래를 대시보드로 실시간 시각화
    

#### 4\. **알림 시스템 연계 (Slack, Email, Webhook)**

*   `process()` 연산자에서 조건 만족 시 external API 호출하여 즉시 알림 전송
    

* * *

### ✅ 마무리 요약

*   이 실습은 Flink에서 가장 기본적인 yet 실용적인 실시간 필터링 + 저장 구조를 구현한 예제다.
    
*   Pandas → PyFlink Stream 변환 → 조건 필터링 → 문자열 포맷 → 콘솔 출력 + FileSink 연결이라는 **스트리밍 분석의 최소 실행 단위**를 학습함
    
*   실무에서는 이 구조에 Kafka, Elasticsearch, 알림 시스템 등을 연계해 **완전한 실시간 이상 탐지 파이프라인**으로 발전시킬 수 있다.
    

* * *

이제 실습 정리가 완벽하게 마무리됐어.  
이제 다음 단계로 Kafka에서 데이터를 직접 받아 실시간 이상 거래를 탐지하고 싶거나,  
Table API 버전으로 확장하거나, 파일 대신 PostgreSQL이나 Elasticsearch로 저장하는 구조로 가보고 싶다면 언제든 도와줄게.

어떤 방향으로 확장해볼까?



---
Powered by [ChatGPT Exporter](https://www.chatgptexporter.com)