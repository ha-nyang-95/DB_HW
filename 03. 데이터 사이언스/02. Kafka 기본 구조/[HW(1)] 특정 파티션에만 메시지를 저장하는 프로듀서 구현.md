# 특정 파티션에만 메시지를 저장하는 프로듀서 구현

📘 1\. 실습 주제 개요
---------------

Kafka는 하나의 토픽(Topic)을 **여러 개의 파티션(Partition)** 으로 분할하여 병렬 처리를 가능하게 하는 구조를 갖는다. 파티션은 **토픽 내부의 데이터 저장 단위**로, 각 파티션은 독립적인 메시지 큐 역할을 하며, 데이터를 순차적으로 저장하고 소비한다.

이번 실습에서는 파티션이 여러 개인 토픽을 생성하고, 각 파티션에 저장된 메시지를 직접 조회함으로써 **Kafka가 메시지를 어떻게 분산 저장하는지**, 그리고 **특정 파티션만 조회하는 방법**을 학습한다. 이를 통해 Kafka의 **확장성과 병렬성의 핵심 메커니즘인 파티셔닝 전략**을 실질적으로 체험할 수 있다.

<br>
<br>

🛠️ 2\. 코드 구조 및 흐름 해설 + 실행 결과 예시 해설
-----------------------------------

### 🔍 토픽 생성 및 구조 확인

```bash
bin/kafka-topics.sh --describe --topic part_test_topic --bootstrap-server localhost:9092
```

*   출력 요약:
    
    ```
    PartitionCount: 3
    ReplicationFactor: 1
    Partition 0 → Leader: 0
    Partition 1 → Leader: 0
    Partition 2 → Leader: 0
    ```
    

👉 총 3개의 파티션을 가진 토픽 `part_test_topic`이 생성되었고, 모든 파티션은 브로커 `0`에 속해 있다.

* * *

### 📥 파티션별 메시지 수신 결과

#### 🔸 Partition 1

```bash
bin/kafka-console-consumer.sh --topic part_test_topic --from-beginning --partition 1 --bootstrap-server localhost:9092
```

*   결과:
    
    ```
    Processed a total of 0 messages
    ```
    

🔍 해당 파티션에는 메시지가 저장되지 않은 상태

<br>

#### 🔸 Partition 2

```bash
bin/kafka-console-consumer.sh --topic part_test_topic --from-beginning --partition 2 --bootstrap-server localhost:9092
```

*   결과:
    
    ```
    Message 1
    Message 2
    Message 3
    Message 4
    Processed a total of 4 messages
    ```
    

🔍 메시지 4건이 파티션 2에 집중되어 저장된 것을 확인할 수 있다.

<br>

#### 🔸 Partition 0

```bash
bin/kafka-console-consumer.sh --topic part_test_topic --from-beginning --partition 0 --bootstrap-server localhost:9092
```

*   결과:
    
    ```
    Message without key 1
    Message without key 2
    Message without key 3
    Processed a total of 3 messages
    ```
    

🔍 메시지 키 없이 보낸 메시지들이 파티션 0에 저장되었음을 확인할 수 있다.

<br>

### ⚠️ 메시지 분산 기준 해설

Kafka는 Producer가 메시지를 전송할 때 다음 순서로 파티션을 결정한다:

1.  **Key가 있는 경우** → Key의 해시값을 기준으로 파티션 결정 (일관성 보장)
    
2.  **Key가 없는 경우** → 라운드로빈 방식 또는 DefaultPartitioner 설정에 따라 순환 분배
    

즉, 위 실습에서 메시지를 **Key 없이 전송**했기 때문에 Kafka가 내부 로직에 따라 파티션을 자동 선택한 결과다.

<br>

⚙️ 3\. 주요 명령어 흐름 + 설명 주석
------------------------

```bash
# 1. Topic 상세 확인
bin/kafka-topics.sh \
  --describe \
  --topic part_test_topic \
  --bootstrap-server localhost:9092

# 2. 파티션 별 메시지 조회
bin/kafka-console-consumer.sh \
  --topic part_test_topic \
  --from-beginning \
  --partition 0 \
  --bootstrap-server localhost:9092
```

> `--partition N` 옵션을 통해 특정 파티션에 저장된 메시지만 필터링하여 조회할 수 있다.

<br>
<br>

📚 4\. 추가 설명 및 실무 팁
-------------------

*   Kafka에서 **파티션 수는 병렬 소비자 수의 최대치**를 결정한다. 즉, 파티션이 3개면 동시에 3개의 consumer 그룹 인스턴스가 병렬로 처리 가능.
    
*   **Key를 명시하지 않고 메시지를 보내면**, 데이터 순서가 보장되지 않으며, 파티션도 예측 불가하게 분배된다. 실무에서는 사용자 ID 또는 주문 번호 등으로 key를 설정해 일관성 있는 파티셔닝을 유도하는 것이 일반적이다.
    
*   Kafka는 내부적으로 메시지를 `offset` 기반으로 관리하며, 각 파티션은 독립적인 offset 시퀀스를 갖는다.
    
*   **토픽 생성 후 파티션 수는 증가 가능하지만 감소는 불가능**하므로 초기에 파티션 수 설정은 신중해야 한다.
    