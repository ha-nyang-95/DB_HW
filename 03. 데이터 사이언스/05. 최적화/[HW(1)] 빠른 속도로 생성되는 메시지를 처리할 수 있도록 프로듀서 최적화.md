# 실습 정리본 작성 요청

**User:** 장철환(하냥) (wkdcjfghks1@gmail.com)  
**Created:** 5/11/2025 11:48  
**Updated:** 5/11/2025 12:27  
**Exported:** 5/11/2025 12:30  

## Response:
좋아, 이 실습은 Kafka 프로듀서의 **전송 성능 최적화 실험**을 직접 수행해보는 아주 좋은 예제야.  
이제 이 실습도 네가 요청한 네 가지 항목에 맞춰, **절대 요약하지 않고**, 각 단계별로 나눠서 정리해줄게.

* * *

📘 1\. 실습 주제 개요
---------------

이번 실습은 Kafka에서 **대량 메시지 전송 시 성능을 결정짓는 주요 설정값들**인 `batch.size`, `compression.type`, `linger.ms`를 조정하면서, 그 변화가 **메시지 전송 속도에 어떤 영향을 주는지**를 실험적으로 확인하는 데 목적이 있다.

Kafka는 고성능 메시지 처리 시스템이지만, **잘못된 설정값**으로 인해 처리량이 낮아지거나, 네트워크와 디스크 자원을 비효율적으로 사용할 수 있다. 본 실습에서는 KafkaProducer 객체의 주요 성능 설정을 아래와 같이 변화시켜가며 10만 개의 메시지를 전송하고, 그에 걸린 시간을 측정하여 성능을 평가한다:

| 설정 항목 | 설명 |
| --- | --- |
| `batch.size` | 메시지를 묶어서 전송하는 최대 크기 (byte 단위) |
| `compression.type` | 메시지 압축 방식 (예: none, gzip, snappy) |
| `linger.ms` | 배치가 꽉 차지 않아도 전송 대기 시간 설정 (ms 단위) |

실무에서 Kafka를 사용하는 경우, 처리량(Throughput)과 지연 시간(Latency)의 균형을 맞추는 것이 매우 중요하다. 이 실습은 그 균형점을 찾는 데 필요한 실험 데이터를 생성하는 데 활용된다.

* * *

이제 다음 메시지에서 **2\. 코드 구조 및 흐름 해설 + 실행 결과 예시 및 해설**을 아주 자세히 설명해줄게.  
계속 진행해도 괜찮지?

## Response:
좋아, 이제 **2\. 코드 구조 및 흐름 해설 + 실행 결과 예시 및 해설**을 아주 구체적으로 정리해줄게.  
이 실습의 핵심은 KafkaProducer 설정값 3가지의 조합에 따라 **대규모 메시지 전송 성능이 어떻게 달라지는지**를 실험적으로 분석하는 거야.

* * *

🛠️ 2\. 코드 구조 및 흐름 해설 + 실행 결과 예시 및 해설
-------------------------------------

* * *

### 🔄 전체 실습 흐름 요약

```
for batch_size in BATCH_SIZES:
    for compression in COMPRESSION_TYPES:
        for linger in LINGER_TIMES:
            → KafkaProducer 생성 (설정 적용)
            → 100,000개의 100B 메시지 전송
            → 전송 시간 측정 및 출력
```

총 실험 케이스 수:  
**3 (batch.size) × 3 (compression.type) × 3 (linger.ms) = 27가지 조합**에 대해 성능을 비교 측정

* * *

### 🔍 코드 흐름 해설

* * *

#### ✅ 메시지 생성 (100바이트 고정)

```python
MESSAGE_PAYLOAD = json.dumps({"data": "A" * (MESSAGE_SIZE - 20)}).encode('utf-8')
```

*   JSON 문자열 구조를 가진 메시지를 생성
    
*   전체 크기가 100바이트가 되도록 `"data"` 필드 값의 길이를 조정
    
*   직렬화된 메시지를 바이너리 형태로 Kafka에 전송
    

* * *

#### ✅ 성능 테스트 루프

```python
for batch_size in BATCH_SIZES:
    for compression in COMPRESSION_TYPES:
        for linger in LINGER_TIMES:
```

*   `batch.size`: KafkaProducer가 네트워크 전송 전 메시지를 묶는 크기 (bytes 단위)
    
    *   너무 작으면 전송이 너무 자주 발생 → 오버헤드 증가
        
    *   너무 크면 대기 시간이 길어짐
        
*   `compression.type`: 메시지 압축 방식
    
    *   `"none"`: 압축 없음 (CPU 사용량↓, 네트워크 사용량↑)
        
    *   `"gzip"`: 높은 압축률, 느림
        
    *   `"snappy"`: 낮은 압축률, 빠름
        
*   `linger.ms`: 배치가 가득 차지 않아도 전송까지 기다리는 시간
    
    *   0이면 메시지 도착 즉시 전송, 클수록 batching 가능성 ↑
        

* * *

#### ✅ KafkaProducer 생성

```python
producer = KafkaProducer(
    bootstrap_servers=BROKER,
    batch_size=batch_size,
    compression_type=compression if compression != "none" else None,
    linger_ms=linger,
    acks=1
)
```

*   설정값을 실제로 Producer에 적용
    
*   `acks=1`: 리더 브로커로부터만 전송 확인을 받으면 됨 (속도 우선)
    

* * *

#### ✅ 메시지 전송 및 측정

```python
start_time = time.time()

for _ in range(NUM_MESSAGES):
    producer.send(TOPIC, MESSAGE_PAYLOAD)

producer.flush()
elapsed_time = time.time() - start_time
```

*   `send()`로 메시지를 비동기 전송
    
*   `flush()` 호출 시, 버퍼에 남은 메시지까지 모두 전송 완료
    
*   총 전송 시간(`elapsed_time`)을 측정하여 성능 평가
    

* * *

#### ✅ 출력 예시

```text
Testing batch.size = 32768, compression = gzip, linger.ms = 10...
Batch size: 32768, Compression: gzip, Linger.ms: 10, Time taken: 4.812 sec
```

*   이 로그가 27회 출력됨 (조합별로 하나씩)
    
*   단위는 초이며, 수치가 낮을수록 전송 효율이 높은 것
    

* * *

### 🎯 실험 결과로 파악할 수 있는 인사이트 예시

| 조합 | 처리 시간 (예시) | 해석 |
| --- | --- | --- |
| batch=16384, comp=none, linger=0 | 7.1초 | 배치 작고 압축도 없음 → 전송 빈도 높음 |
| batch=65536, comp=gzip, linger=50 | 3.9초 | 압축 효율↑ + 대기시간↑ → 네트워크 효율적 |
| batch=32768, comp=snappy, linger=10 | 4.2초 | 균형 있는 선택, 실무에서 자주 사용 |

* * *

이제 다음 메시지에서, 이 전체 실습 코드를 기반으로 **3\. 전체 코드 + 상세 주석**을 정리해서 제공할게.  
지금까지 한 것처럼 **줄 하나도 생략하지 않고 모든 라인에 상세한 설명을 달아줄게**.  
바로 이어서 진행할게.

## Response:
좋아, 이제 **3\. 전체 코드 + 상세 주석**을 제공할게.  
이 코드는 성능 실험의 핵심이므로 **모든 설정, 반복, 시간 측정, 메시지 생성**에 대해 정확하고 실무 수준의 주석을 달아서 설명할게.

* * *

⚙️ 3\. 전체 코드 + 상세 주석
--------------------

```python
# %%
"""
Kafka 프로듀서의 성능을 최적화하는 실습입니다.

TODO:
1. Kafka 프로듀서를 생성하고 `batch.size`, `compression.type`, `linger.ms` 값을 변경하며 메시지를 전송합니다.
2. 서로 다른 설정에서 메시지 처리 속도를 비교합니다.
3. 메시지를 모두 보낼 때까지 걸린 시간을 출력합니다.
"""

from kafka import KafkaProducer          # KafkaProducer: 메시지를 Kafka로 전송하기 위한 클래스
import time                              # 시간 측정을 위한 표준 라이브러리
import json                              # JSON 형식의 메시지를 생성하기 위한 라이브러리

# %%
# 설정 값
BROKER = "localhost:9092"               # Kafka 브로커 주소
TOPIC = "test-topic"                    # 테스트용 Kafka 토픽 이름
BATCH_SIZES = [16384, 32768, 65536]     # 배치 크기 (16KB, 32KB, 64KB)
COMPRESSION_TYPES = ["none", "gzip", "snappy"]  # 압축 방식 종류
LINGER_TIMES = [0, 10, 50]              # Linger.ms 설정값 (ms 단위)
NUM_MESSAGES = 100000                   # 전송할 메시지 개수
MESSAGE_SIZE = 100                      # 메시지 1개당 크기 (바이트 기준)

# %%
# TODO 1: 100바이트 크기의 JSON 메시지를 생성
# Kafka 메시지의 총 크기를 100바이트로 제한하기 위해 "data" 필드의 문자열 길이를 조절
MESSAGE_PAYLOAD = json.dumps({
    "data": "A" * (MESSAGE_SIZE - 20)   # JSON 구조상 여유 공간을 고려하여 20바이트 제외
}).encode('utf-8')                      # KafkaProducer는 바이트 문자열을 전송하므로 UTF-8 인코딩 수행

# %%
# TODO 2: 서로 다른 설정에서 메시지 처리 속도를 비교
# 세 가지 설정(batch, 압축, linger)의 모든 조합을 테스트
for batch_size in BATCH_SIZES:
    for compression in COMPRESSION_TYPES:
        for linger in LINGER_TIMES:
            print(f"Testing batch.size = {batch_size}, compression = {compression}, linger.ms = {linger}...")

            # TODO 3: Kafka 프로듀서를 생성하고 설정 변경
            # 설정값을 적용한 KafkaProducer 인스턴스 생성
            producer = KafkaProducer(
                bootstrap_servers=BROKER,                 # 브로커 주소
                batch_size=batch_size,                    # 배치 크기
                compression_type=compression if compression != "none" else None,  # 압축 방식 적용
                linger_ms=linger,                         # linger.ms 설정
                acks=1                                    # 리더 브로커로부터의 응답만 받으면 OK (속도 우선)
            )

            # TODO 4: 메시지 전송 시작 시간 기록
            start_time = time.time()  # 현재 시간 기록 (초 단위, float)

            # TODO 5: NUM_MESSAGES 개수만큼 메시지 전송
            for _ in range(NUM_MESSAGES):
                producer.send(TOPIC, MESSAGE_PAYLOAD)  # 메시지를 비동기적으로 전송

            # TODO 6: 모든 메시지 전송 완료 후 시간 측정
            producer.flush()  # 내부 버퍼에 남아있는 메시지 강제 전송
            elapsed_time = time.time() - start_time  # 총 소요 시간 계산

            # TODO 7: 결과 출력
            print(f"Batch size: {batch_size}, Compression: {compression}, Linger.ms: {linger}, Time taken: {elapsed_time:.3f} sec\n")

            # TODO 8: 테스트 간 간격 추가
            time.sleep(2)  # 브로커에 과부하가 가지 않도록 테스트 간 2초 대기
```

* * *

이제 이 코드는 실험 설정, 전송 절차, 측정, 출력까지 모든 구성 요소에 대해 **명확하게 주석이 달린 완성도 높은 실험 코드**가 되었어.

다음 메시지에서는 이 실험을 기반으로 한 **📚 4\. 추가 설명 및 실무 팁**을 정리해줄게.  
지금까지의 결과를 해석하고, 실무에서 어떤 상황에 어떻게 활용되는지를 자세히 설명할게.  
계속 진행할게.

## Response:
좋아, 이제 마지막 항목인 **📚 4\. 추가 설명 및 실무 팁**을 제공할게.  
이 항목에서는 이 실습이 실제 Kafka 운영 환경에서 어떤 의미를 가지는지, 각 설정이 어떻게 성능에 영향을 미치는지, 그리고 실무에서는 어떻게 최적화 결정을 내리는지를 구체적으로 설명할 거야.

* * *

📚 4\. 추가 설명 및 실무 팁
-------------------

* * *

### ✅ 각 설정값의 성능 영향 요약

| 설정 항목 | 설명 | 성능 영향 요약 |
| --- | --- | --- |
| `batch.size` | 전송 전에 묶는 메시지의 최대 크기 | **크면 전송 횟수 줄고 처리량 증가**, 너무 크면 지연 시간 증가 |
| `compression.type` | 메시지 압축 방식 (`none`, `gzip`, `snappy`) | **압축률 높으면 네트워크 사용↓**, CPU 부하↑. gzip은 가장 느림 |
| `linger.ms` | 메시지를 보내기 전 대기 시간 (밀리초) | **길면 배치 전송 기회↑ → 처리 효율↑**, 하지만 지연 시간도 늘어남 |

* * *

### 🧪 실험 결과 해석 시 고려 요소

*   \*\*처리 속도(Throughput)\*\*와 \*\*지연 시간(Latency)\*\*은 **서로 트레이드오프** 관계
    
*   `linger.ms = 0`은 지연은 최소지만 **비효율적인 네트워크 사용**
    
*   `batch.size`가 너무 작으면 전송이 너무 자주 발생 → 오버헤드 ↑
    
*   압축을 적용하면 처리량은 높아지지만, **브로커와 컨슈머에 더 많은 CPU 자원 요구**
    

* * *

### 💼 실무 적용 예시

| 상황 | 추천 설정 |
| --- | --- |
| 실시간 로그 수집 (지연 민감) | `batch.size = 16KB`, `compression = none`, `linger.ms = 0` |
| 데이터 적재 파이프라인 (지연 허용, 처리량 우선) | `batch.size = 64KB`, `compression = gzip`, `linger.ms = 50` |
| 대규모 트래픽 분석 (균형형) | `batch.size = 32KB`, `compression = snappy`, `linger.ms = 10` |

* * *

### 🧨 실무에서 자주 발생하는 실수 및 주의사항

| 실수 | 원인 및 해결 방법 |
| --- | --- |
| ❌ 처리 속도가 지나치게 낮음 | 너무 작은 batch, linger 설정 → 네트워크 호출이 지나치게 많아짐 |
| ❌ 메시지 순서가 뒤섞임 | 파티션 수가 여러 개일 때 Key가 없으면 순서 보장 안됨 |
| ❌ 메시지 유실 우려 | `acks=0` 또는 flush 없이 종료 → 메시지가 전송되지 않고 종료될 수 있음 |
| ❌ flush 생략 | 실험 시간 정확도 떨어짐 → 마지막 메시지들이 전송되지 않음 |

* * *

### 📈 추가 확장 아이디어

*   **Matplotlib 또는 Seaborn을 활용한 설정별 처리 시간 시각화**
    
    *   x축: 설정 조합, y축: 처리 시간 (초)
        
    *   시각적으로 어떤 설정이 가장 빠른지 파악 가능
        
*   **Excel로 결과 내보내기**
    
    *   `csv.writer`로 처리 시간 로그를 파일로 저장 후 비교 분석
        
*   **다중 브로커 환경에서의 테스트**
    
    *   브로커 수에 따라 성능 분산 효과가 달라질 수 있음
        
*   **Producer throughput benchmarking tool**
    
    *   `kafka-producer-perf-test.sh` 스크립트로 같은 실험을 커맨드라인에서 수행 가능
        

* * *

### ✅ 마무리 요약

이 실습은 Kafka 프로듀서 성능의 핵심 설정을 조정하면서 성능에 미치는 영향을 직접 측정한 예제로,  
**실시간 처리, 고속 적재, 병목 진단 등 다양한 시나리오에서 최적의 설정을 선택할 수 있도록 해주는 기초 실험 환경**이자,  
**Kafka 운영 튜닝 역량의 핵심 기반을 형성하는 매우 중요한 실습**이야.

* * *

이제 모든 항목이 완성됐어.  
이 실험 데이터를 바탕으로 **CSV 저장, 그래프 시각화, 보고서 포맷 구성** 등으로 확장해도 좋고,  
다음 Kafka 관련 심화 주제(예: 프로듀서 재시도 설정, 브로커 장애 복구 실험, Flink 연동 실시간 처리 등)로 넘어가도 좋아.

다음 단계로 뭐 하고 싶어?



---
Powered by [ChatGPT Exporter](https://www.chatgptexporter.com)