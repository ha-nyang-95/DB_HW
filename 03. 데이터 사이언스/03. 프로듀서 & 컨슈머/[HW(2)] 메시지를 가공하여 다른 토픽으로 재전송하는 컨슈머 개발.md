# 메시지를 가공하여 다른 토픽으로 재전송하는 컨슈머 개발

📘 1\. 실습 주제 개요
---------------

이번 실습의 목적은 Kafka 스트리밍 시스템을 통해 다음과 같은 **데이터 흐름 파이프라인을 직접 구축**하고 동작을 검증하는 것이다:

```
KafkaProducer → input-topic → KafkaConsumer (변환) → output-topic → KafkaConsumer (최종 확인)
```

이 실습은 Kafka가 단순 메시지 큐를 넘어, **데이터 처리와 전달을 동시에 수행할 수 있는 실시간 스트리밍 인프라**로서 어떻게 동작하는지를 이해하는 데 중점을 둔다.

실습의 흐름은 다음과 같다:

1.  **input-topic**, **output-topic** 두 개의 토픽을 생성한다.
    
2.  KafkaProducer가 input-topic에 원본 메시지를 전송한다.
    
3.  KafkaConsumer가 input-topic에서 메시지를 소비하여 변환(예: 대문자화) 후, KafkaProducer를 통해 output-topic으로 전송한다.
    
4.  최종 KafkaConsumer가 output-topic을 구독하여 변환된 메시지를 확인한다.
    

이러한 구성은 Flink나 Spark Streaming 없이도, Python 기반으로 Kafka의 end-to-end 스트리밍 구조를 이해하고 실험하는 좋은 출발점이 된다. 실무에서는 이 구조가 ETL 스트림, 사용자 행동 데이터 처리, 실시간 로그 파이프라인 등에 그대로 응용된다.

<br>
<br>

🛠️ 2\. 코드 구조 및 흐름 해설 + 실행 결과 예시 및 해설
-------------------------------------


### 🧩 \[PART 1\] Kafka 토픽 초기화 및 테스트 메시지 전송

#### 🔧 구조 개요

1.  `KafkaAdminClient`로 기존 토픽 삭제 및 재생성
    
2.  `KafkaProducer`로 `input-topic`에 메시지 전송
    

#### ⚙️ 실행 흐름

```python
admin_client = KafkaAdminClient(...)
admin_client.delete_topics(["input-topic", "output-topic"])
admin_client.create_topics([
    NewTopic(name="input-topic", num_partitions=1, replication_factor=1),
    NewTopic(name="output-topic", num_partitions=1, replication_factor=1)
])
```

*   메시지가 흐를 토픽 2개를 새로 생성
    
*   단일 파티션이므로 메시지는 순차적으로 저장됨
    

```python
producer = KafkaProducer(...)
test_messages = ["hello", "world", "kafka", "streaming", "data"]
for message in test_messages:
    producer.send("input-topic", value=message)
```

*   총 5개의 문자열 메시지가 input-topic에 전송됨
    
*   메시지 순서와 내용을 고정시켜 검증 가능하게 구성
    

#### ✅ 예상 출력

```
Sent: hello
Sent: world
Sent: kafka
Sent: streaming
Sent: data
```

<br>

### 🧩 \[PART 2\] 변환된 메시지를 output-topic으로 전송하는 중간 Processor

#### 🔧 구조 개요

1.  `KafkaConsumer`가 `input-topic`에서 메시지 수신
    
2.  문자열을 대문자로 변환
    
3.  `KafkaProducer`가 `output-topic`으로 재전송
    

#### ⚙️ 실행 흐름

```python
for message in consumer:
    transformed_message = message.value.decode('utf-8').upper()
    producer.send("output-topic", value=transformed_message)
```

*   메시지를 실시간으로 읽고 바로 가공 처리
    
*   대문자 변환은 여기서 "변환 로직" 역할을 수행
    
*   실무에서는 이 위치에 텍스트 분석, 필터링, 분기 로직 등이 들어간다
    

#### ✅ 예상 출력 (터미널 로그)

```
Transformed and Sent: HELLO
Transformed and Sent: WORLD
Transformed and Sent: KAFKA
Transformed and Sent: STREAMING
Transformed and Sent: DATA
```

<br>

### 🧩 \[PART 3\] 최종 메시지 수신자 (Output Consumer)

#### 🔧 구조 개요

*   단순한 KafkaConsumer가 `output-topic`을 구독하여 최종 변환된 메시지를 수신함
    
*   ETL 파이프라인의 “Load” 단계와 동일한 역할
    

#### ⚙️ 실행 흐름

```python
for message in consumer:
    print(f"Consumed from output-topic: {message.value.decode('utf-8')}")
```

#### ✅ 예상 출력

```
Consumed from output-topic: HELLO
Consumed from output-topic: WORLD
Consumed from output-topic: KAFKA
Consumed from output-topic: STREAMING
Consumed from output-topic: DATA
```

<br>
<br>

⚙️ 3\. 전체 코드 + 상세 주석
--------------------


### 🧩 PART 1: Kafka 토픽 삭제 후 생성 및 input-topic에 메시지 전송

```python
# %%
"""
Kafka 프로듀서를 활용하여 `input-topic`에 테스트 메시지를 전송하는 실습입니다.

TODO:
1. kafka-python 라이브러리를 사용하여 KafkaAdminClient를 생성합니다.
2. 기존 `input-topic`과 `output-topic`이 존재하면 삭제한 후, 새로 생성합니다.
3. KafkaProducer를 사용하여 `input-topic`에 테스트 메시지를 전송합니다.
"""

import time  # 토픽 삭제 후 잠깐 대기용
from kafka import KafkaProducer  # 메시지 전송을 위한 KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic  # 토픽 관리에 필요한 라이브러리

# %%
# TODO 1: KafkaAdminClient를 생성하세요.
admin_client = KafkaAdminClient(
    bootstrap_servers='localhost:9092',  # Kafka 브로커 주소 (localhost 환경)
    client_id='test-admin'               # 클라이언트 식별 ID
)

# 토픽 이름을 변수로 정의
input_topic = "input-topic"
output_topic = "output-topic"

# %%
# TODO 2: 기존 `input-topic`과 `output-topic`을 삭제한 후, 2초 대기 후 새로 생성하세요.
existing_topics = admin_client.list_topics()  # 현재 Kafka 서버에 존재하는 토픽 목록 조회

# 기존 토픽이 있다면 삭제 수행
for topic in [input_topic, output_topic]:
    if topic in existing_topics:
        admin_client.delete_topics([topic])  # 삭제 요청
        print(f"기존 토픽 '{topic}' 삭제 완료")
        time.sleep(2)  # Kafka 내부 토픽 정리 시간을 위해 대기

# 새 토픽을 생성: input-topic과 output-topic 모두 파티션 1개, 복제 1개로 구성
admin_client.create_topics([
    NewTopic(name=input_topic, num_partitions=1, replication_factor=1),
    NewTopic(name=output_topic, num_partitions=1, replication_factor=1)
])
print(f"새로운 토픽 '{input_topic}' 및 '{output-topic}' 생성 완료")

# Admin 클라이언트 종료
admin_client.close()

# %%
# TODO 3: KafkaProducer를 생성하세요.
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',            # Kafka 브로커 주소
    value_serializer=lambda v: v.encode('utf-8')   # 문자열을 바이트로 직렬화
)

# %%
# TODO 4: `input-topic`에 테스트 메시지를 전송하세요.
test_messages = ["hello", "world", "kafka", "streaming", "data"]  # 테스트 메시지 목록

# 메시지를 반복하며 input-topic에 전송
for message in test_messages:
    producer.send(input_topic, value=message)  # 메시지를 input-topic으로 전송
    print(f"Sent: {message}")  # 전송 확인 로그
```

<br>
<br>

### 🧩 PART 2: `input-topic`에서 메시지를 수신하고 대문자로 변환 후 `output-topic`으로 송신

```python
# %%
"""
Kafka 컨슈머를 활용하여 `input-topic`의 메시지를 변환 후 `output-topic`으로 전송하는 실습입니다.

TODO:
1. kafka-python 라이브러리를 사용하여 KafkaConsumer를 생성합니다.
2. KafkaProducer를 생성하여 변환된 메시지를 `output-topic`으로 전송합니다.
3. `input-topic`에서 메시지를 소비한 후 특정 변환 로직을 적용하여 `output-topic`으로 다시 송신합니다.
"""

from kafka import KafkaConsumer, KafkaProducer  # KafkaConsumer와 KafkaProducer 동시 사용

# %%
# TODO 1: KafkaConsumer를 생성하세요.
consumer = KafkaConsumer(
    "input-topic",  # 메시지를 구독할 대상 토픽 (원본 메시지 위치)
    bootstrap_servers='localhost:9092',  # Kafka 브로커 주소
    auto_offset_reset='earliest',        # 오프셋 초기화 방식 ('earliest'는 처음부터 메시지를 읽음)
    enable_auto_commit=True,            # 메시지 소비 후 자동으로 offset 커밋
    group_id='transform-group',         # Consumer Group 설정 (변환 전용 그룹)
)

# %%
# TODO 2: KafkaProducer를 생성하세요.
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',             # Kafka 브로커 주소
    value_serializer=lambda v: v.encode('utf-8')    # 문자열을 바이트로 직렬화
)

# %%
# TODO 3: `input-topic`의 메시지를 변환 후 `output-topic`으로 전송하세요.
for message in consumer:  # input-topic에서 메시지를 지속적으로 소비
    # 수신한 메시지를 UTF-8 문자열로 디코딩하고 대문자로 변환
    transformed_message = message.value.decode('utf-8').upper()

    # 변환된 메시지를 output-topic으로 전송
    producer.send("output-topic", value=transformed_message)

    # 콘솔 로그로 결과 출력
    print(f"Transformed and Sent: {transformed_message}")
```

<br>
<br>

### 🧩 PART 3: `output-topic`에서 메시지를 수신하여 최종 결과 출력

```python
# %%
"""
Kafka 컨슈머를 활용하여 `output-topic`의 메시지를 소비하고 출력하는 실습입니다.

TODO:
1. kafka-python 라이브러리를 사용하여 KafkaConsumer를 생성합니다.
2. `output-topic`을 구독하고, 메시지를 소비합니다.
3. 소비한 메시지를 출력하여 변환된 데이터가 정상적으로 수신되었는지 확인합니다.
"""

from kafka import KafkaConsumer  # KafkaConsumer 클래스 import

# %%
# TODO 1: KafkaConsumer를 생성하세요.
consumer = KafkaConsumer(
    "output-topic",  # 구독할 대상 토픽 (변환 후 메시지 위치)
    bootstrap_servers='localhost:9092',  # Kafka 브로커 주소
    auto_offset_reset='earliest',        # 처음부터 메시지를 읽음
    enable_auto_commit=True,             # 자동 offset 커밋 설정
    group_id='final-check-group'         # 소비자 그룹 ID (최종 확인용)
)

# %%
# TODO 2: `output-topic`에서 메시지를 소비하고 출력하세요.
for message in consumer:  # output-topic에서 메시지를 하나씩 소비
    # 수신한 메시지를 UTF-8로 디코딩하여 문자열로 변환 후 출력
    print(f"Consumed from output-topic: {message.value.decode('utf-8')}")
```

<br>
<br>

📚 4\. 추가 설명 및 실무 팁
-------------------


### ✅ 실무에서 이 구조가 쓰이는 대표 사례

| 목적                      | 사용 예시                                          |
| ------------------------- | -------------------------------------------------- |
| 실시간 데이터 전처리      | 사용자 클릭 로그를 대문자화/정제                   |
| 메시지 변환 파이프라인    | IoT 센서 데이터 단위 변환, 필터링                  |
| 간단한 스트림 연산        | 텍스트 마스킹, 통계 전처리                         |
| 마이크로 서비스 간 브릿지 | input-topic → 서비스A → output-topic 구조로 모듈화 |

<br>

### 🧩 Kafka 파이프라인 구성 시 주의사항

1.  **토픽 삭제 후 생성은 실습 환경에서만 사용 가능**
    
    *   운영 환경에서는 절대 추천되지 않음.
        
    *   대신 `KafkaAdminClient.describe_topics()`로 토픽 상태를 점검하고, 필요하면 명시적 이름 변경을 통해 토픽을 새로 만듦.
        
2.  **오프셋 초기화 설정 (`auto_offset_reset`) 주의**
    
    *   `'earliest'`: 토픽의 가장 오래된 메시지부터 소비
        
    *   `'latest'`: 현재 시점 이후의 메시지만 소비
        
    *   실습에서는 `'earliest'`가 유리하지만, 운영 환경에서는 상황에 따라 적절히 선택해야 함.
        
3.  **`value_serializer`, `value_deserializer` 설정 필수**
    
    *   Kafka는 메시지를 바이트로 전송하므로, `str`, `json`, `dict` 형태의 메시지를 보내려면 **반드시 직렬화 설정**이 필요함
        
    *   예: `value_serializer=lambda v: json.dumps(v).encode('utf-8')`
        
4.  **컨슈머 그룹의 오프셋 커밋 정책**
    
    *   `enable_auto_commit=True`이면 메시지를 읽자마자 커밋함. 하지만 **메시지를 처리하기 전에 실패하면 손실 위험** 있음
        
    *   실무에선 `enable_auto_commit=False`로 설정하고, 처리 후 `consumer.commit()`을 직접 호출하는 방식이 일반적
        
5.  **KafkaProducer는 send() 후 flush() 또는 close() 고려**
    
    *   `producer.send(...)` 호출은 비동기적으로 메시지를 버퍼에 넣기 때문에, **종료 전에 `flush()` 또는 `close()` 호출이 필요**
        
    *   실습 코드에서 생략되었지만, 실무에선 아래처럼 보완:
        
        ```python
        producer.flush()
        producer.close()
        ```
        

<br>

### ⚙️ 확장 방향 (실무 적용)

1.  **Kafka → Flink or Spark 연동**
    
    *   input-topic을 Flink가 읽어서 복잡한 집계 처리 후 output-topic으로 전송 가능
        
2.  **Kafka Connect로 DB 연동**
    
    *   output-topic 메시지를 PostgreSQL, MongoDB, Elasticsearch 등으로 바로 연동
        
3.  **Schema Registry를 통한 메시지 유효성 검증**
    
    *   실무에서는 메시지 구조를 Avro/JSON Schema로 관리해서 데이터 일관성을 확보
        
4.  **Docker Compose 기반 Kafka 테스트 환경 구축**
    
    *   현재는 로컬 `localhost:9092` 기반이지만, 컨테이너 기반 Kafka 환경으로 전환 시 협업이 훨씬 수월해짐
        

<br>

### 🧨 자주 하는 실수 요약

| 실수                             | 원인 및 해결 방법                                  |
| -------------------------------- | -------------------------------------------------- |
| 메시지가 Consumer에 안 들어옴    | offset 설정 오류 (`latest`인데 기존 메시지만 있음) |
| 메시지 깨짐 (UnicodeDecodeError) | 직렬화/디코딩 설정 누락                            |
| send()는 했지만 브로커에 없음    | flush(), close() 누락                              |
| 메시지 순서가 꼬임               | 파티션이 여러 개인데 Key 설정이 없음               |
