
# ✅ Kafka 메시지 분산 실습 정리본

## 📌 실습 목적
Kafka에서 메시지를 보낼 때,
- **Key 없이 전송한 메시지**는 어떻게 파티션에 분산되는지
- **Key를 지정해서 전송한 메시지**는 항상 같은 파티션에 저장되는지
- **다른 Key로 전송했을 때**, 파티션이 어떻게 달라지는지  
를 확인하는 실습입니다.

---

## 🔧 실습 환경 초기화

### 1. 기존 토픽 삭제 & 재생성 (3개의 파티션으로)
```bash
bin/kafka-topics.sh --delete --topic part_test_topic --bootstrap-server localhost:9092

bin/kafka-topics.sh --create --topic part_test_topic --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
```

### 2. 토픽 구조 확인
```bash
bin/kafka-topics.sh --describe --topic part_test_topic --bootstrap-server localhost:9092
```

✅ 기대 결과:
- Partition 0 ~ 2까지 생성됨
- Leader, Replicas, Isr 모두 0 (단일 브로커이므로 정상)

---

## 📨 메시지 전송

### 1. **Key 없이 메시지 전송**
```bash
bin/kafka-console-producer.sh --topic part_test_topic --bootstrap-server localhost:9092
```

전송한 내용:
```
Message without key 1
Message without key 2
Message without key 3
```

> 💡 Key가 없으면 Kafka가 **라운드로빈 방식**으로 파티션에 분산함  
(단, 버전/환경에 따라 하나의 파티션에 몰릴 수도 있음)

---

### 2. **Key를 지정하여 메시지 전송**
```bash
bin/kafka-console-producer.sh --topic part_test_topic --bootstrap-server localhost:9092 --property "parse.key=true" --property "key.separator=:"
```

전송한 내용:
```
key1:Message 1
key1:Message 2
key1:Message 3
key2:Message 4
```

> 💡 key1 메시지 3개는 **항상 동일한 파티션**에 저장됨  
> 💡 key2는 다른 해시값을 가지므로 다른 파티션에 들어갈 가능성이 있음

---

## 🔍 파티션별 메시지 확인

```bash
# Partition 0
bin/kafka-console-consumer.sh --topic part_test_topic --bootstrap-server localhost:9092 --from-beginning --partition 0
```
출력 예시:
```
Message without key 1
Message without key 2
Message without key 3
```

```bash
# Partition 1
bin/kafka-console-consumer.sh --topic part_test_topic --bootstrap-server localhost:9092 --from-beginning --partition 1
```
출력 예시:
```
Message 4
```

```bash
# Partition 2
bin/kafka-console-consumer.sh --topic part_test_topic --bootstrap-server localhost:9092 --from-beginning --partition 2
```
출력 예시:
```
Message 1
Message 2
Message 3
```

---

## 📊 결과 정리

| 메시지 내용               | 키      | 저장된 파티션 |
|--------------------------|---------|----------------|
| Message without key 1~3  | 없음    | 0번            |
| Message 1~3              | key1    | 2번            |
| Message 4                | key2    | 1번            |

> ❗ key2가 Partition 1로 간 이유:  
Kafka는 key의 **해시값을 기준으로 파티션을 자동 할당**하므로, key마다 저장되는 파티션이 달라질 수 있음.

---

## 📘 핵심 개념 복습용 요약

| 조건            | 파티션 배정 기준                                  |
|-----------------|--------------------------------------------------|
| Key 없음        | 기본적으로 라운드로빈 (환경에 따라 다를 수 있음) |
| Key 있음        | `hash(key) % 파티션 수` → 항상 같은 파티션에 저장됨 |
| Key 다름        | 다른 파티션으로 분산될 가능성 있음                |

---

## ✅ 마무리 팁

- 실습 결과가 예시 이미지와 다를 수 있는 건 자연스러운 현상입니다.
- 중요한 건 **원리**를 이해하고, **key가 파티션에 영향을 미친다**는 걸 증명하는 것입니다.
- 시험에서는 **분산 로직의 이해와 결과 분석 능력**이 더 중요합니다.
