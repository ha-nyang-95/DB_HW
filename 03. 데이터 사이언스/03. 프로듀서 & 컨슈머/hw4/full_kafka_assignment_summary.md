# 📘 Kafka 실습 과제 완벽 복습 노트 (비전공자용 초상세 버전)

---

## ✅ 0. Kafka란 무엇인가?

Kafka는 데이터를 한 쪽에서 보내고, 다른 쪽에서 받아서 처리하는 **데이터 파이프라인** 도구예요.  
쉽게 말해, **“전달자 역할을 하는 메시지 통신 시스템”**입니다.

Kafka에는 3가지 주요 구성요소가 있어요:

| 구성요소 | 설명 |
|----------|------|
| **Producer** | 메시지를 만들어 Kafka에 보냄 |
| **Consumer** | Kafka에서 메시지를 꺼내서 처리 |
| **Topic** | 메시지를 분류해서 저장하는 통로 (메일함 이름처럼 생각하면 됨) |

---

## 🎯 과제 목표 요약

Kafka를 활용해서 다음과 같은 흐름을 직접 구현해보는 실습입니다.

1. `input-topic`과 `output-topic`이라는 **두 개의 Kafka 토픽**을 생성한다.
2. `input-topic`에 문자열 메시지들(예: `"hello"`, `"world"`)을 Kafka Producer로 보낸다.
3. Kafka Consumer가 `input-topic`에서 메시지를 읽은 후, **대문자로 변환**한다.
4. 변환된 메시지를 Kafka Producer를 통해 `output-topic`에 다시 보낸다.
5. 또 다른 Kafka Consumer가 `output-topic`에서 메시지를 읽어서 **최종적으로 출력**한다.

---

## 📂 전체 구성 파일 개요

| 파일명 | 역할 |
|--------|------|
| `input_producer_skeleton.py` | 토픽 생성 + 테스트 메시지 전송 |
| `output_producer_skeleton.py` | 메시지 소비 후 변환 + 재전송 |
| `output_consumer_skeleton.py` | 최종 메시지 소비 및 출력 |

---

## 🧩 1. input_producer_skeleton.py 상세 설명

### ✅ 이 파일의 목적
- Kafka에 사용할 **두 개의 토픽**을 만든다: `input-topic`, `output-topic`
- `input-topic`에 **테스트용 문자열 메시지**를 여러 개 보낸다

### 📌 내부 흐름 순서

#### 1. Kafka 관리자 객체 생성

```python
from kafka.admin import KafkaAdminClient
admin_client = KafkaAdminClient(bootstrap_servers='localhost:9092', client_id='test-admin')
```

#### 2. 기존 토픽 삭제

```python
existing_topics = admin_client.list_topics()
for topic in [input_topic, output_topic]:
    if topic in existing_topics:
        admin_client.delete_topics([topic])
```

#### 3. 새 토픽 생성

```python
from kafka.admin import NewTopic
admin_client.create_topics([
    NewTopic(name=input_topic, num_partitions=1, replication_factor=1),
    NewTopic(name=output_topic, num_partitions=1, replication_factor=1)
])
```

#### 4. Kafka Producer 생성 및 메시지 전송

```python
from kafka import KafkaProducer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: v.encode('utf-8')
)
```

#### 5. 메시지 전송

```python
test_messages = ["hello", "world", "kafka", "streaming", "data"]
for message in test_messages:
    producer.send(input_topic, value=message)
```

---

## 🧩 2. output_producer_skeleton.py 상세 설명

### ✅ 이 파일의 목적
- input-topic에서 메시지를 읽는다 (Kafka Consumer)
- 대문자로 변환한다 (예: "hello" → "HELLO")
- output-topic으로 다시 보낸다 (Kafka Producer)

### 📌 내부 흐름 순서

#### 1. Kafka Consumer 생성 (input-topic 구독)

```python
consumer = KafkaConsumer(
    "input-topic",
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='transform-group',
    value_deserializer=lambda v: v.decode('utf-8')
)
```

#### 2. Kafka Producer 생성

```python
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: v.encode('utf-8')
)
```

#### 2. 메시지 변환 및 재전송

```python
for message in consumer:
    transformed_message = message.value.upper()
    producer.send("output-topic", value=transformed_message)
```

---

## 🧩 3. output_consumer_skeleton.py 상세 설명

### ✅ 이 파일의 목적
- output-topic에서 메시지를 읽고 터미널에 출력

### 📌 내부 흐름 순서

#### 1. Kafka Consumer 생성

```python
consumer = KafkaConsumer(
    "output-topic",
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='final-check-group',
    value_deserializer=lambda v: v.decode('utf-8')
)
```

#### 2. 메시지 출력

```python
for message in consumer:
    print(f"Consumed from output-topic: {message.value}")
```

---

## 🛠️ 실행 순서 요약

#### 1. Kafka 서버가 실행 중이어야 한다.
#### 2. 터미널에서 순서대로 실행
```bash
# 토픽 생성 + 메시지 전송
python input_producer_skeleton.py
# 메시지 읽기 + 대문자 변환 + 재전송
python output_producer_skeleton.py
# 최종 메시지 확인
python output_consumer_skeleton.py
```

---

## 🧨 오류 & 문제 해결 요약

| 오류 | 원인 | 해결 방법 |
|------|------|------------|
| `python not found` | Ubuntu에선 python3만 설치됨 | `python3` 사용 |
| `No module named 'kafka'` | kafka-python 설치 안 됨 | `pip install kafka-python` |
| `No module named 'distutils'` | Python 3.12에서 distutils 없음 | Python 3.10으로 변경 |
| `list_topics()()` 오류 | 괄호 2번으로 함수처럼 호출됨 | `list_topics()`로 수정 |
| 메시지가 안 나옴 | 메시지를 이미 소비함 | `group_id` 새로 지정하거나 메시지 재전송 |

---

## ✅ 핵심 개념 요약

| 개념 | 설명 |
|------|------|
| Kafka | 메시지를 주고받는 스트리밍 시스템 |
| Topic | 메시지를 담는 통로 (메일함 같은 것) |
| Producer | Kafka에 메시지를 보내는 주체 |
| Consumer | Kafka에서 메시지를 꺼내는 주체 |
| group_id | 메시지를 공유하는 소비자 그룹 이름 |
| serializer | 문자열 → byte 변환 |
| deserializer | byte → 문자열 변환 |
| offset | Kafka 메시지를 얼마나 읽었는지 추적하는 기준 |

---

## 🔁 다음에 혼자 복습할 때 순서

1. Kafka 서버 실행
2. Python 3.10 가상환경 만들기
3. `pip install kafka-python`
4. input_producer 실행 → 메시지 전송
5. output_producer 실행 → 메시지 변환 후 전송
6. output_consumer 실행 → 최종 메시지 확인