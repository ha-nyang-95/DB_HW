# 여러 컨슈머를 실행하여 하나의 토픽을 동시에 구독하는 실습

📘 1\. 실습 주제 개요
---------------

Kafka는 **Consumer Group**이라는 독특한 메시지 처리 구조를 갖고 있다. 일반적인 메시지 큐와 달리, Kafka에서는 여러 Consumer들이 하나의 그룹으로 묶여 **협업하여 데이터를 처리**할 수 있으며, 이 구조는 대규모 실시간 처리에 매우 유리하다.

이번 실습은 하나의 토픽에 여러 메시지를 전송하고, 동일한 Consumer Group에 소속된 Consumer들이 메시지를 나누어 소비하는 방식과, **다른 그룹으로 메시지를 다시 소비하는 재처리 방식**을 실습을 통해 확인하는 것이다. 이 과정을 통해 Kafka의 **확장성과 재처리 유연성**을 명확히 이해할 수 있다.

<br>
<br>

🛠️ 2\. 코드 구조 및 흐름 해설 + 실행 결과 예시 해설
-----------------------------------

### 🔁 흐름 구성

```
Kafka Topic (consumer_test_topic1)
  └── Group A: test-group (2 consumers) → 메시지를 분산 소비
  └── Group B: new-group (1 consumer)  → 모든 메시지 재소비 (from-beginning)
```

* * *

### ✅ Group A - test-group (두 Consumer로 분산 처리)

```bash
bin/kafka-console-consumer.sh \
  --topic consumer_test_topic1 \
  --bootstrap-server localhost:9092 \
  --group test-group
```

*   첫 번째 터미널 출력:
    
    ```
    Consumer Test Message 1
    Consumer Test Message 3
    ```
    
*   두 번째 터미널 출력:
    
    ```
    Consumer Test Message 2
    ```
    

🔍 **동일한 Consumer Group에 속한 Consumer들 간에 메시지가 자동으로 나눠져**서 소비되는 것을 확인할 수 있다. 이는 Kafka가 각 Consumer에게 **서로 다른 파티션 또는 메시지를 배분**하기 때문이다.

<br>

### 🔄 Group B - new-group (재처리 확인)

```bash
bin/kafka-console-consumer.sh \
  --topic consumer_test_topic1 \
  --bootstrap-server localhost:9092 \
  --group new-group \
  --from-beginning
```

*   출력 결과:
    
    ```
    Consumer Test Message 2
    Consumer Test Message 1
    Consumer Test Message 3
    ```
    

🔍 **새로운 그룹(new-group)** 은 해당 토픽에 대한 **기존 소비 이력이 없기 때문에** 전체 메시지를 처음부터 읽을 수 있다. `--from-beginning` 옵션을 통해 과거 데이터까지 모두 소비할 수 있음.

<br>
<br>

⚙️ 3\. 주요 명령어 흐름 + 상세 설명
------------------------

```bash
# 동일한 그룹으로 두 Consumer 실행
bin/kafka-console-consumer.sh \
  --topic consumer_test_topic1 \
  --bootstrap-server localhost:9092 \
  --group test-group

# 새로운 그룹으로 전체 메시지 다시 소비
bin/kafka-console-consumer.sh \
  --topic consumer_test_topic1 \
  --bootstrap-server localhost:9092 \
  --group new-group \
  --from-beginning
```

> `--group` 옵션을 통해 Consumer Group 이름을 지정하고, `--from-beginning`은 메시지를 처음부터 다시 읽게 해준다. 이는 로그 기반 스트리밍에서 **데이터 재처리**를 위한 중요한 기능이다.

<br>
<br>

📚 4\. 추가 설명 및 실무 팁
-------------------

*   Kafka에서 **Consumer Group은 메시지 소비 단위**다. 즉, Group ID가 다르면 서로 간섭 없이 같은 데이터를 별도로 소비할 수 있다.
    
*   **하나의 파티션은 오직 하나의 Consumer에게만 할당**되므로, 파티션 수보다 Consumer 수가 많으면 일부 Consumer는 유휴 상태가 된다.
    
*   실무에서는 데이터를 처음부터 다시 처리해야 할 경우, 기존 Group ID를 변경하거나, 같은 Group으로 `--reset-offsets` 도구를 활용한다.
    
*   Kafka는 메시지를 삭제하지 않고 저장(log)하는 구조이기 때문에, **소비자가 소비한 위치(offset)를 기준으로 재처리가 가능**하다.
    
