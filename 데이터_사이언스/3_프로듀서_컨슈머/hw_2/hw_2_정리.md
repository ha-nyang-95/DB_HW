# Kafka Python 실습 정리 (비전공자용)

> 목표: Kafka 토픽을 만들고, 같은 키로 메시지를 보내고, 파티션을 확인하는 실습 완료하기                  
> 환경: WSL2 (Ubuntu), Python, VS Code                  
> **WSL**       
> 가상 운영 체제(또 하나의 윈도우라 생각하면 편함)          
> **venv**       
> 가상 환경(어떤 모듈도 깔려있지 않은 깡통)     
> 가상 환경을 사용하는 이유는 기존 환경에서 추가 모듈을 설치했을 때         
> 발생할 수 있는 충돌을 사전 대비하기 위해서이다.

---

## ✅ 전체 흐름 요약

| 단계 | 내용 | 결과 |
|------|------|------|
| 1단계 | Kafka & Zookeeper 실행 | Kafka 서버 준비 완료 |
| 2단계 | Python 가상환경 만들기 | 안전하게 라이브러리 설치 가능 |
| 3단계 | kafka-python 설치 | Python에서 Kafka 사용 가능 |
| 4단계 | 토픽 생성 (`create_topic.py`) | 파티션 3개짜리 토픽 생성 |
| 5단계 | 메시지 전송 (`send_messages.py` / `producer_skeleton.py`) | 같은 키로 메시지 전송 |
| 6단계 | 메시지 읽기 (`consumer1/2_skeleton.py`) | 같은 파티션에 들어가는지 확인 |

---

## 🛠️ 실습 상세 과정 + 코드

### 📌 1. Kafka 실행 준비

```bash
# Zookeeper 실행 (터미널 1)
cd /usr/local/kafka
bin/zookeeper-server-start.sh config/zookeeper.properties

# Kafka 실행 (터미널 2)
cd /usr/local/kafka
bin/kafka-server-start.sh config/server.properties
```

### ❗ 에러 해결 (NodeExistsException 발생 시)
```bash
cd /usr/local/kafka
bin/zookeeper-shell.sh localhost:2181

# 쉘 접속 후
deleteall /brokers/ids/0
quit
```

---

### 📌 2. 가상환경 만들기 & 라이브러리 설치

```bash
cd ~
mkdir kafka-python-test
cd kafka-python-test

# venv 설치 에러 발생 시
sudo apt update
sudo apt install python3.12-venv

# 가상환경 생성 및 실행
python3 -m venv venv
source venv/bin/activate

# kafka-python 설치
pip install kafka-python
```

---

### 📌 3. 토픽 생성 코드 (`producer_skeleton.py`의 상단 부분)

```python
from kafka.admin import KafkaAdminClient, NewTopic

admin_client = KafkaAdminClient(
    bootstrap_servers="localhost:9092",
    client_id='test-admin'
)

topic_name = "test-topic"
existing_topics = admin_client.list_topics()

if topic_name in existing_topics:
    admin_client.delete_topics([topic_name])
    time.sleep(2)

new_topic = NewTopic(name=topic_name, num_partitions=3, replication_factor=1)
admin_client.create_topics([new_topic])
admin_client.close()
```

---

### 📌 4. 메시지 전송 코드 (`producer_skeleton.py` 하단 부분)

```python
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    key_serializer=str.encode,
    value_serializer=str.encode
)

topic_name = "test-topic"
keys = ["key1", "key2", "key3"]

for i in range(10):
    key = keys[i % len(keys)]
    value = f"message-{i}"
    producer.send(topic_name, key=key, value=value)
    print(f"Sent: {value} with key: {key}")

producer.flush()
```

---

### 📌 5. 메시지 소비 코드 (공통)

#### consumer1_skeleton.py (같은 group으로 실행 시 한 번만 수신)
```python
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    "test-topic",
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='my-group'
)

for message in consumer:
    print(f"[Consumer1] Partition={message.partition}, Key={message.key.decode('utf-8')}, Value={message.value.decode('utf-8')}")
```

#### consumer2_skeleton.py (다른 group_id 설정 시 같은 메시지도 수신 가능)
```python
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    "test-topic",
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='my-group-2'
)

for message in consumer:
    print(f"[Consumer2] Partition={message.partition}, Key={message.key.decode('utf-8')}, Value={message.value.decode('utf-8')}")
```

---

## ✅ 결과 예시
```
[Consumer1] Partition=1, Key=key2, Value=message-1
[Consumer1] Partition=1, Key=key2, Value=message-4
...
[Consumer2] Partition=2, Key=key3, Value=message-2
```

- 동일한 키는 항상 같은 파티션에 들어감 ✅
- Consumer group이 다르면 동일 메시지를 동시에 수신 가능

---

## 🧠 미래의 나에게

- Kafka는 Zookeeper와 Kafka 서버가 동시에 실행되어야 함
- Python에서는 kafka-python 라이브러리를 통해 쉽게 다룰 수 있음
- 같은 key 값이면 Kafka는 해시 기반으로 동일한 파티션에 메시지를 넣음
- Python에서 한글 또는 문자열을 전송할 땐 `.encode()` 필요함 (또는 `serializer` 설정)
- 실습 구조를 알면 나중에 JSON 메시지 처리, 파티션 전략 테스트, 로그 분석 등으로 확장 가능!

---

> 📂 실습 코드 경로 예시: `~/kafka-python-test` 또는 `data_science2_hw_3_2/skeleton`
> 
> 이 실습을 통해 Kafka의 핵심 원리를 이해하고, 분산 시스템의 흐름을 몸으로 익혔다 💪


---

## ▶️ Kafka 실습 실행 순서 (전체 요약)

### ✅ 1단계: 터미널 2개 열기

- **터미널 1:** Zookeeper 실행
- **터미널 2:** Kafka 실행

---

### ✅ 2단계: 터미널 1 - Zookeeper 실행

```bash
cd /usr/local/kafka
bin/zookeeper-server-start.sh config/zookeeper.properties
```

---

### ✅ 3단계: 터미널 2 - Kafka 실행

```bash
cd /usr/local/kafka
bin/kafka-server-start.sh config/server.properties
```

---

### ✅ 4단계: 터미널 3 (또는 새 탭) 열기

> 메시지 전송 및 토픽 생성을 위한 Python 코드 실행 준비

(선택) 가상환경 다시 활성화:
```bash
cd ~/kafka-python-test
source venv/bin/activate
```

---

### ✅ 5단계: 토픽 생성 및 메시지 전송

```bash
python3 producer_skeleton.py
```

- 토픽이 이미 있으면 삭제 후 새로 생성
- `key1`, `key2`, `key3` 키로 메시지 10개 전송

---

### ✅ 6단계: Consumer 실행

#### 터미널 4에서 consumer1 실행
```bash
python3 consumer1_skeleton.py
```

#### 터미널 5에서 consumer2 실행
```bash
python3 consumer2_skeleton.py
```

> 메시지가 어느 파티션에 들어가는지, 어떤 Consumer가 받는지 확인 가능

---

## 🧠 실행 중 자주 쓰는 명령어 정리

| 상황 | 명령어 |
|------|--------|
| 가상환경 재실행 | `source venv/bin/activate` |
| Kafka 에러 발생 | `zookeeper-shell.sh`로 접속 후 `/brokers/ids/0` 삭제 |
| 디렉토리 이동 | `cd ~/kafka-python-test` |
| 파이썬 코드 실행 | `python3 파일명.py` |

---
