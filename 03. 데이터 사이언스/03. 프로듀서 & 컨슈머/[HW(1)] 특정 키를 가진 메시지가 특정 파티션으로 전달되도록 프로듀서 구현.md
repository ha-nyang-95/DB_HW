# 특정 키를 가진 메시지가 특정 파티션으로 전달되도록 프로듀서 구현

📘 1\. 실습 주제 개요
---------------

Kafka는 메시지를 여러 파티션에 분산 저장함으로써 높은 처리량과 병렬 소비를 실현한다. 이때, 메시지에 **Key를 지정하면 해당 Key를 기준으로 해시 함수를 적용해 특정 파티션에 메시지를 보내는 구조**를 가진다. 동일한 Key는 항상 동일한 파티션으로 전송되기 때문에, 이 구조는 **순서 보장**과 **세션 일관성**이 필요한 실무 상황에서 유용하게 쓰인다.

이번 실습은 `kafka-python` 라이브러리를 통해 직접 KafkaProducer와 KafkaConsumer를 구현하고, **동일한 Key를 가진 메시지가 동일한 파티션에 저장 및 소비되는지**를 검증하는 실험이다.

<br>
<br>

🛠️ 2\. 코드 구조 및 흐름 해설 + 실행 결과 예시 해설
-----------------------------------

### 🔨 KafkaAdminClient로 Topic 재생성 (파티션 3개)

```python
admin_client = KafkaAdminClient(...)
admin_client.delete_topics([topic_name])
admin_client.create_topics([NewTopic(name=topic_name, num_partitions=3, ...)])
```

*   기존 `test-topic`이 존재하면 삭제 후,
    
*   **파티션 3개로 새로 생성**해, 키 기반 분산이 명확히 나타나도록 설정한다.
    

<br>

### 📤 Producer: 키를 명시해 메시지 전송

```python
keys = ["key1", "key2", "key3"]
for i in range(10):
    key = keys[i % len(keys)]
    value = f"message-{i}"
    producer.send(topic_name, key=key, value=value)
```

*   메시지는 총 10개 전송되고, 키는 `"key1", "key2", "key3"` 순환
    
*   Kafka 내부적으로 각 키는 **hash(key) % num\_partitions** 로 파티션이 결정됨
    
*   따라서 동일 키는 동일 파티션으로 분배되어야 함
    

<br>
<br>

### 📥 Consumer: 키, 값, 파티션 출력

```python
for message in consumer:
    print(f"...Key: {message.key.decode()}, Partition: {message.partition}")
```

*   **동일한 키가 동일 파티션에 들어가는지 검증** 가능
    
*   예상 예시:
    
    ```
    Received: message-0, Key: key1, Partition: 1
    Received: message-3, Key: key1, Partition: 1
    ...
    ```
    
*   결과적으로 `key1`은 항상 파티션 1로, `key2`는 0번, `key3`은 2번 파티션으로 매핑되는 등, **일관된 파티셔닝 결과**가 도출된다면 Kafka의 키 해싱 방식이 정확히 적용된 것이다.
    

<br>
<br>

⚙️ 3\. 전체 코드 + 상세 주석
--------------------

### 🔧 KafkaAdminClient: 토픽 삭제 및 재생성

```python
import time
from kafka.admin import KafkaAdminClient, NewTopic

# Kafka 관리 클라이언트를 생성합니다.
admin_client = KafkaAdminClient(
    bootstrap_servers="localhost:9092",  # Kafka 브로커 주소
    client_id='test-admin'               # 클라이언트 식별자
)

topic_name = "test-topic"

# 기존 토픽이 존재하면 삭제하고 2초 대기합니다.
existing_topics = admin_client.list_topics()
if topic_name in existing_topics:
    admin_client.delete_topics([topic_name])
    print(f"기존 토픽 '{topic_name}' 삭제 완료")
    time.sleep(2)

# 파티션 3개, 복제 계수 1로 새 토픽 생성
new_topic = NewTopic(name=topic_name, num_partitions=3, replication_factor=1)
admin_client.create_topics([new_topic])
print(f"새로운 토픽 '{topic_name}' 생성 완료")

# AdminClient 종료
admin_client.close()
```

<br>

### ✉️ KafkaProducer: 키 기반 메시지 전송

```python
from kafka import KafkaProducer

# Kafka 프로듀서를 생성합니다.
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    key_serializer=str.encode,   # 문자열 키를 바이트로 인코딩
    value_serializer=str.encode  # 문자열 값을 바이트로 인코딩
)

# 세 가지 키를 순환하며 메시지를 전송합니다.
keys = ["key1", "key2", "key3"]
for i in range(10):
    key = keys[i % len(keys)]            # key1, key2, key3 반복
    value = f"message-{i}"               # 메시지 내용 생성
    producer.send(topic_name, key=key, value=value)  # 전송
    print(f"Sent: {value} with key: {key}")
```

<br>

### 📥 KafkaConsumer #1

```python
from kafka import KafkaConsumer

# Kafka 컨슈머를 생성합니다.
consumer = KafkaConsumer(
    "test-topic",
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',  # 가장 처음 메시지부터 소비
    enable_auto_commit=True,       # 오프셋 자동 커밋
    group_id='my-group'            # 그룹 ID 설정
)

# 메시지를 지속적으로 소비하고 파티션 정보를 확인합니다.
for message in consumer:
    print(f"Received: {message.value.decode('utf-8')}, "
          f"Key: {message.key.decode('utf-8')}, "
          f"Partition: {message.partition}")
```

<br>

### 📥 KafkaConsumer #2 (그룹 ID만 다름)

```python
consumer = KafkaConsumer(
    "test-topic",
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='my-group-2'  # 그룹 ID를 다르게 지정
)

for message in consumer:
    print(f"Received: {message.value.decode('utf-8')}, "
          f"Key: {message.key.decode('utf-8')}, "
          f"Partition: {message.partition}")
```

<br>
<br>

📚 4\. 추가 설명 및 실무 팁
-------------------

*   **Kafka의 파티셔닝 전략**은 기본적으로 `hash(key) % partition_count`를 따른다. 따라서 키가 같으면 파티션도 같지만, 키가 없으면 라운드 로빈으로 분산된다.
    
*   실무에서 **사용자 ID, 세션 ID, 주문번호** 등을 key로 설정하면 **동일한 소비자가 해당 메시지를 처리할 수 있어 상태 일관성 유지에 효과적**이다.
    
*   `KafkaProducer`에서 `key_serializer`, `KafkaConsumer`에서 `key_deserializer`를 꼭 맞춰주지 않으면 메시지를 제대로 인코딩/디코딩하지 못한다.
    
*   파티션 개수는 향후 **스케일업 시 병목 방지를 위해 충분히 넉넉히 설정**하는 것이 좋다. 단, 파티션 수는 늘릴 수 있어도 줄일 수는 없다.
    
