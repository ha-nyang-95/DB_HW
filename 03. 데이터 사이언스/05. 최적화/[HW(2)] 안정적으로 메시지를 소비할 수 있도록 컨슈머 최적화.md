# 안정적으로 메시지를 소비할 수 있도록 컨슈머 최적화

📘 1\. 실습 주제 개요
---------------

이번 실습의 목적은 Kafka 컨슈머가 메시지를 소비할 때 사용하는 주요 설정값들을 조정하면서, **메시지 소비 속도(처리량)** 에 어떤 영향을 미치는지 측정하는 것이다.  
Kafka Consumer는 메시지를 서버로부터 가져오는 방식에서 다음 세 가지 설정값의 영향을 많이 받는다:

| 설정 항목 | 설명 |
| --- | --- |
| `max.poll.records` | 한 번의 poll() 호출로 가져올 수 있는 최대 메시지 개수 |
| `fetch.min.bytes` | 최소한 이만큼의 데이터가 모일 때까지 fetch 요청을 대기 |
| `fetch.max.wait.ms` | 데이터가 충분하지 않아도 이 시간 이상 기다리면 fetch 응답 |

이 실습에서는 Kafka 토픽에서 **총 10만 개의 메시지를 소비**하며, 각 설정 조합마다 **소요된 시간**을 측정해 비교한다.  
이를 통해 다음과 같은 실무 감각을 익힐 수 있다:

*   실시간 스트리밍 시스템에서 **최적의 fetch 조건**을 설정하는 기준
    
*   **지연을 줄이고 처리량을 높이는 균형점**을 찾는 방법
    
*   다양한 Kafka 설정이 실제 퍼포먼스에 미치는 영향에 대한 실증적 이해
    

<br>
<br>

🛠️ 2\. 코드 구조 및 흐름 해설 + 실행 결과 예시 및 해설
-------------------------------------

### 🔄 전체 실습 흐름 요약

```text
for max.poll.records in [10, 100, 500]:
    for fetch.min.bytes in [1KB, 10KB, 50KB]:
        for fetch.max.wait.ms in [100, 500, 1000]:
            → KafkaConsumer 생성
            → 100,000개 메시지 소비
            → 소요 시간 측정
            → 결과 출력
```

총 실험 케이스 수:  
**3 (poll.records) × 3 (fetch.min.bytes) × 3 (fetch.max.wait.ms) = 27가지 조합**을 측정

<br>

### 🔍 코드 흐름 설명

#### ✅ 실험 설정 목록

```python
POLL_RECORDS = [10, 100, 500]
FETCH_MIN_BYTES = [1024, 10240, 51200]
FETCH_MAX_WAIT = [100, 500, 1000]
NUM_MESSAGES = 100000
```

*   `max.poll.records`: 한 번의 `poll()` 호출로 읽어올 최대 메시지 수
    
    *   클수록 한 번에 더 많은 메시지를 가져와 효율 ↑, 단 메모리 사용량도 증가
        
*   `fetch.min.bytes`: 브로커가 최소 이만큼 데이터가 모이기 전까지 응답을 기다림
    
    *   클수록 대기 후 큰 덩어리를 한 번에 가져옴 → Throughput ↑, Latency ↑
        
*   `fetch.max.wait.ms`: 데이터가 없더라도 이 시간만큼 기다린 후 응답을 강제로 보냄
    
    *   지연 보상 설정: `min.bytes` 조건을 너무 오래 기다리지 않도록 제한
        

<br>

#### ✅ KafkaConsumer 생성

```python
consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=BROKER,
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    max_poll_records=poll_records,
    fetch_min_bytes=fetch_min,
    fetch_max_wait_ms=fetch_wait
)
```

*   `auto_offset_reset='earliest'`: 토픽에 오프셋 정보가 없으면 처음부터 읽음
    
*   `enable_auto_commit=True`: 메시지를 읽은 후 자동으로 오프셋 커밋
    
*   나머지 설정값은 실험 변수로 주기적으로 변경됨
    

<br>

#### ✅ 메시지 소비 & 측정

```python
start_time = time.time()

message_count = 0
for message in consumer:
    message_count += 1
    if message_count >= NUM_MESSAGES:
        break

elapsed_time = time.time() - start_time
```

*   Kafka 컨슈머는 내부적으로 `poll()`을 반복하면서 메시지를 가져온다
    
*   10만 개 메시지를 읽을 때까지 반복
    
*   `time.time()`으로 시작~끝 시간 측정
    

<br>

#### ✅ 출력 예시 (결과 로그)

```text
Testing max.poll.records = 100, fetch.min.bytes = 10240, fetch.max.wait.ms = 500...
Max poll records: 100, Fetch min bytes: 10240, Fetch max wait: 500, Time taken: 5.217 sec
```

*   각 설정 조합별로 처리에 걸린 시간이 초 단위로 출력됨
    
*   가장 빠른 조합을 찾는 것이 목적
    

<br>

### 🎯 예상 결과 해석 예시

| 설정 조합 | 결과 | 해석 |
| --- | --- | --- |
| poll=10, min=1024, wait=100 | 7.1초 | 너무 자주 fetch 발생 → 비효율 |
| poll=500, min=51200, wait=500 | 4.3초 | 덩어리 크게, 자주 안 가져옴 → Throughput ↑ |
| poll=100, min=10240, wait=1000 | 4.7초 | 균형 잡힌 조합 (실무 선호) |

<br>
<br>

⚙️ 3\. 전체 코드 + 상세 주석
--------------------

```python
# %%
"""
Kafka 컨슈머의 성능을 최적화하는 실습입니다.

TODO:
1. Kafka 컨슈머를 생성하고 `max.poll.records`, `fetch.min.bytes`, `fetch.max.wait.ms` 값을 변경하며 메시지를 소비합니다.
2. 서로 다른 설정에서 메시지 소비 속도를 비교합니다.
3. 메시지를 모두 소비할 때까지 걸린 시간을 출력합니다.
"""

from kafka import KafkaConsumer   # Kafka로부터 메시지를 읽어오는 Consumer 클래스
import time                       # 처리 시간 측정을 위한 시간 모듈

# %%
# 설정 값 정의
BROKER = "localhost:9092"         # Kafka 브로커 주소
TOPIC = "test-topic"              # 테스트용 Kafka 토픽
POLL_RECORDS = [10, 100, 500]     # 한 번의 poll()에서 최대 가져올 메시지 수
FETCH_MIN_BYTES = [1024, 10240, 51200]  # 최소 fetch 크기: 1KB, 10KB, 50KB
FETCH_MAX_WAIT = [100, 500, 1000]       # 최대 fetch 대기 시간: 100ms, 500ms, 1000ms
NUM_MESSAGES = 100000            # 실험 대상 총 메시지 수

# %%
# TODO 1: 설정 조합마다 실험을 반복
for poll_records in POLL_RECORDS:
    for fetch_min in FETCH_MIN_BYTES:
        for fetch_wait in FETCH_MAX_WAIT:
            # 현재 조합을 로그로 출력
            print(f"Testing max.poll.records = {poll_records}, fetch.min.bytes = {fetch_min}, fetch.max.wait.ms = {fetch_wait}...")

            # TODO 2: KafkaConsumer 생성
            consumer = KafkaConsumer(
                TOPIC,                           # 구독할 Kafka 토픽
                bootstrap_servers=BROKER,        # Kafka 브로커 주소
                auto_offset_reset='earliest',    # 가장 처음부터 메시지를 소비
                enable_auto_commit=True,         # 자동 오프셋 커밋 활성화
                max_poll_records=poll_records,   # 한 번의 poll에서 가져올 최대 메시지 수
                fetch_min_bytes=fetch_min,       # 최소로 가져올 메시지 바이트 수
                fetch_max_wait_ms=fetch_wait     # 위 크기가 안 되더라도 대기 후 가져올 최대 시간
            )

            # TODO 3: 처리 시간 측정을 위한 시작 시간 기록
            start_time = time.time()

            # TODO 4: 메시지를 반복적으로 소비하면서 개수를 카운트
            message_count = 0
            for message in consumer:
                message_count += 1
                if message_count >= NUM_MESSAGES:
                    break  # 10만 개 도달 시 종료

            # TODO 5: 총 소비 시간 측정
            elapsed_time = time.time() - start_time

            # TODO 6: 실험 결과 출력
            print(
                f"Max poll records: {poll_records}, "
                f"Fetch min bytes: {fetch_min}, "
                f"Fetch max wait: {fetch_wait}, "
                f"Time taken: {elapsed_time:.3f} sec\n"
            )

            # TODO 7: 테스트 간 간격 두기 (브로커 과부하 방지)
            time.sleep(2)
```

<br>
<br>

📚 4\. 추가 설명 및 실무 팁
-------------------

### ✅ 설정값별 성능 영향 요약

| 설정 항목 | 설명 | 실무적 의미 |
| --- | --- | --- |
| `max.poll.records` | 한 번에 가져올 수 있는 메시지 최대 개수 | 너무 작으면 잦은 I/O 발생, 너무 크면 처리 지연 가능 |
| `fetch.min.bytes` | 최소 이만큼 데이터를 모은 후 전송 | 큼 → Throughput↑, Latency↑ (대량 전송에 유리) |
| `fetch.max.wait.ms` | 기다릴 수 있는 최대 시간 | 크면 응답 대기 가능성↑, 짧으면 즉시 반환으로 지연↓ |

<br>

### 🔬 실험 결과 해석 가이드

| 결과 유형 | 해석 |
| --- | --- |
| 처리 시간이 매우 짧음 | 최적의 배치 크기와 네트워크 요청 빈도 설정 조합 |
| 처리 시간이 지나치게 김 | 메시지를 너무 자주, 너무 적게 가져오고 있을 가능성 |
| 조합마다 편차 심함 | 특정 설정값이 병목 지점으로 작용 중 |

💡 **Tip**: 실무에서는 처리 시간뿐 아니라 **CPU 사용량, 메모리 소비, GC 빈도** 등을 함께 측정해야 진짜 성능을 파악할 수 있음

<br>

### ⚠️ 실무에서 자주 발생하는 실수

| 실수 | 원인 및 해결 방법 |
| --- | --- |
| ❌ 메시지를 너무 조금씩 가져옴 | `max.poll.records` 값이 너무 낮거나 `fetch.min.bytes`가 작음 |
| ❌ 너무 오래 기다림 | `fetch.max.wait.ms`가 커서 지연 발생 |
| ❌ poll 속도보다 처리 속도가 느림 | 메시지가 쌓이기 시작하고, Consumer Lag이 급증함 |
| ❌ 오프셋 손실 또는 중복 처리 | `enable_auto_commit=True`일 때 처리 중 실패 발생 시 중복 처리 위험 존재 |

<br>

### 🧠 실무 최적화 전략 예시

| 운영 목적 | 설정 조합 예시 |
| --- | --- |
| 실시간 처리 (지연 최소화) | `max.poll.records=100`, `fetch.min.bytes=1024`, `fetch.max.wait.ms=100` |
| 대량 로그 적재 (처리량 우선) | `max.poll.records=500`, `fetch.min.bytes=51200`, `fetch.max.wait.ms=1000` |
| 안정성과 속도 균형 | `max.poll.records=100`, `fetch.min.bytes=10240`, `fetch.max.wait.ms=500` |

<br>

### 🔁 확장 아이디어

*   **KafkaConsumer.poll() 내부 처리량 측정**
    
    *   poll 호출 횟수 및 poll당 메시지 수 측정
        
*   **Matplotlib, Seaborn을 활용한 속도 시각화**
    
    *   조합별 처리 시간을 선형 그래프, heatmap 등으로 시각화
        
*   **KafkaConsumer 성능 모니터링 로그 수집**
    
    *   처리 시간 외에도 `records.lag`, `fetch-latency-avg` 등 지표 수집
        
*   **멀티 Consumer 성능 비교**
    
    *   동일 설정으로 여러 Consumer 인스턴스 병렬 실행 시 처리 속도 비교
        

<br>

### ✅ 결론: 이 실습의 실무적 의의

이 실습을 통해 다음과 같은 실무 역량을 기를 수 있다:

*   Kafka 컨슈머의 처리량 및 지연 시간에 영향을 주는 핵심 파라미터 이해
    
*   실험적 접근을 통한 성능 최적화 분석 능력
    
*   처리 속도 기반으로 설정 조정 전략 수립
    
*   Kafka 클러스터의 리소스 사용 효율성을 높이는 설정 설계
    
