
# Kafka 실습 가이드 (WSL + Ubuntu 환경 기준)

Kafka 설치부터 실습까지 **혼자서도 문제없이 진행**할 수 있도록 순서대로 설명드립니다.

---

## ✅ 1단계: Java 설치

```bash
sudo apt update
sudo apt install -y openjdk-11-jdk wget unzip
```

---

## ✅ 2단계: Kafka 다운로드 및 설치

```bash
cd ~  # 홈 디렉토리로 이동

wget https://downloads.apache.org/kafka/2.13-3.8.1/kafka_2.13-3.8.1.tgz
tar -xvzf kafka_2.13-3.8.1.tgz
cd kafka_2.13-3.8.1
```

---

## ✅ 3단계: Kafka 3.7.0 버전으로 재설치 (안정 버전 사용 시)

```bash
wget https://archive.apache.org/dist/kafka/3.7.0/kafka_2.13-3.7.0.tgz
tar -xvzf kafka_2.13-3.7.0.tgz
cd kafka_2.13-3.7.0
```

---

## ✅ 4단계: Zookeeper 실행

### 새 Ubuntu 터미널을 열고 아래 명령어 실행

```bash
cd /usr/local/kafka
bin/zookeeper-server-start.sh config/zookeeper.properties

# cd ~/kafka_2.13-3.7.0
# bin/zookeeper-server-start.sh config/zookeeper.properties
```

---

## ✅ 5단계: Kafka 서버 실행

### 다른 터미널에서 아래 명령어 실행

```bash
cd /usr/local/kafka
bin/kafka-server-start.sh config/server.properties

# cd ~/kafka_2.13-3.7.0
# bin/kafka-server-start.sh config/server.properties
```

---

## ❗ 왜 두 개의 터미널이 필요한가요?

| 서버 종류 | 설명 | 실행 위치 |
|----------|------|-----------|
| Zookeeper | Kafka 백엔드 서비스 | Ubuntu 터미널 1 |
| Kafka 서버 | 실제 메시지를 주고받는 서버 | Ubuntu 터미널 2 |

모든 Kafka 명령은 **Ubuntu 터미널**에서 실행하세요. PowerShell은 사용하지 않습니다.

---

## ✅ 6단계: 실습 시작

### 1. 토픽 생성

```bash
bin/kafka-topics.sh --create --topic part_test_topic --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
```

### 2. 토픽 정보 확인

```bash
bin/kafka-topics.sh --describe --topic part_test_topic --bootstrap-server localhost:9092
```

---

## ✅ 7단계: 메시지 전송 실험

### (1) 키 없이 메시지 전송

```bash
bin/kafka-console-producer.sh --topic part_test_topic --bootstrap-server localhost:9092
>Message without key 1
>Message without key 2
>Message without key 3
```

### (2) 키를 포함한 메시지 전송

```bash
bin/kafka-console-producer.sh --topic part_test_topic --bootstrap-server localhost:9092 --property "parse.key=true" --property "key.separator=:"
>key1:Message 1
>key1:Message 2
>key1:Message 3
>key2:Message 4
```

---

## ✅ 8단계: 파티션별 메시지 확인

```bash
# Partition 0 확인
bin/kafka-console-consumer.sh --topic part_test_topic --bootstrap-server localhost:9092 --from-beginning --partition 0

# Partition 1 확인
bin/kafka-console-consumer.sh --topic part_test_topic --bootstrap-server localhost:9092 --from-beginning --partition 1

# Partition 2 확인
bin/kafka-console-consumer.sh --topic part_test_topic --bootstrap-server localhost:9092 --from-beginning --partition 2
```

> ✅ **key1**은 항상 **같은 파티션**에, key 없이 전송한 메시지는 **균등 분산**됩니다.

---

## ✅ 9단계: 토픽 삭제 (재실습을 위해)

```bash
bin/kafka-topics.sh --delete --topic part_test_topic --bootstrap-server localhost:9092
```

---

## 📝 정리

- Zookeeper, Kafka, 실습용 CLI는 모두 **서로 다른 터미널**에서 실행해야 함
- Key가 같은 메시지는 동일 파티션에 저장됨
- Key가 없으면 Kafka가 **Round-Robin 방식**으로 파티션을 자동 분배함
- 실습 시 **토픽 삭제 후 재생성**하여 실험 가능
