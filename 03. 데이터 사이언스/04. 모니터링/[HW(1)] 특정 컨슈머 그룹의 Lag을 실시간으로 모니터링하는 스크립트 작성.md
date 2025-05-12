# 특정 컨슈머 그룹의 Lag을 실시간으로 모니터링하는 스크립트 작성

📘 1\. 실습 주제 개요
---------------

이번 실습의 목표는 **Kafka의 Consumer Lag을 실시간으로 모니터링**하고, 일정 기준을 초과하면 자동으로 경고를 출력하는 시스템을 구축하는 것이다.  
Kafka Exporter는 Kafka 브로커 및 컨슈머 관련 지표를 Prometheus 포맷으로 노출하고, Prometheus는 이를 수집하여 시계열로 저장하거나 알람 기준으로 활용할 수 있게 한다.

이 실습은 Kafka에서 흔히 발생하는 **메시지 적체(Lag)** 상황을 감지하고, 운영자가 빠르게 대응할 수 있도록 돕는다. 특히 다음과 같은 상황에서 중요한 역할을 한다:

*   컨슈머가 죽어서 메시지를 읽지 못하는 경우
    
*   처리 속도가 메시지 유입 속도보다 느릴 때
    
*   특정 파티션에 부하가 몰리는 경우
    

이를 위해 Python 스크립트에서 Prometheus 메트릭 API를 주기적으로 호출하여 특정 Consumer Group의 지연량(Lag)을 수집하고, 설정한 임계값을 초과하면 **경고 메시지를 출력**하는 구조를 구현한다.

<br>
<br>

🛠️ 2\. 코드 구조 및 흐름 해설 + 실행 결과 예시 및 해설
-------------------------------------


### 🧩 전체 흐름 요약

1.  `requests.get()`으로 Kafka Exporter의 Prometheus 메트릭 HTTP 엔드포인트에 접근
    
2.  `kafka_consumergroup_lag{...}` 포맷의 메트릭 라인 중 특정 Consumer Group의 값만 필터링
    
3.  각 파티션에서 수집된 Lag 값을 합산하여 전체 Lag을 계산
    
4.  설정한 임계값 이상일 경우 경고 메시지를 출력
    
5.  이 과정을 일정 시간 간격으로 반복
    

<br>

### 🔍 주요 구성 요소 설명

#### ✅ 설정 영역

```python
PROMETHEUS_URL = "http://localhost:9308/metrics"
CONSUMER_GROUP = 'assignment-group'
LAG_THRESHOLD = 100
CHECK_INTERVAL = 5
```

*   `PROMETHEUS_URL`: Kafka Exporter가 노출하는 Prometheus 포맷 메트릭 주소
    
*   `CONSUMER_GROUP`: 모니터링 대상 컨슈머 그룹 이름
    
*   `LAG_THRESHOLD`: 경고 메시지를 출력할 기준 Lag
    
*   `CHECK_INTERVAL`: 몇 초마다 확인할지 주기 설정
    

<br>

#### ✅ 함수 정의 – `get_consumer_lag()`

```python
def get_consumer_lag():
    response = requests.get(PROMETHEUS_URL)
    lines = response.text.split('\n')
    total_lag = 0
    for line in lines:
        if f'kafka_consumergroup_lag{{consumergroup="{CONSUMER_GROUP}"' in line:
            lag_value = float(line.split()[-1])
            total_lag += lag_value
    return total_lag
```

*   `requests.get(...)`: Prometheus 포맷 메트릭 데이터를 문자열로 받아옴
    
*   `lines = response.text.split('\n')`: 한 줄씩 나누어 리스트화
    
*   `if ... in line`: 모니터링하려는 `assignment-group`에 해당하는 라인만 필터링
    
*   `float(line.split()[-1])`: 각 메트릭 라인의 마지막 항목이 수치 값 (Lag) 이므로 이를 float으로 변환
    
*   `total_lag += lag_value`: 각 파티션에서의 Lag 값을 누적하여 전체 그룹의 Lag 총합 반환
    

<br>

#### ✅ 반복 모니터링 로직

```python
while True:
    lag = get_consumer_lag()
    print(f"Current Lag for {CONSUMER_GROUP}: {lag}")

    if lag >= LAG_THRESHOLD:
        print("WARNING: Consumer Lag is too high!")

    time.sleep(CHECK_INTERVAL)
```

*   무한 루프 안에서 `get_consumer_lag()` 호출
    
*   현재 Lag 값을 실시간 출력
    
*   Lag이 설정한 임계값보다 크면 경고 문구 출력
    
*   주기적 반복을 위해 `time.sleep(...)`으로 간격 설정
    

<br>

### 🖥️ 실행 결과 예시

(컨슈머가 정상적으로 메시지를 읽고 있지 않은 경우)

```
Current Lag for assignment-group: 243.0
WARNING: Consumer Lag is too high!
Current Lag for assignment-group: 258.0
WARNING: Consumer Lag is too high!
Current Lag for assignment-group: 266.0
WARNING: Consumer Lag is too high!
```

(정상적으로 컨슈머가 처리하는 경우)

```
Current Lag for assignment-group: 2.0
Current Lag for assignment-group: 0.0
```

이처럼 간단한 콘솔 출력만으로도 Kafka 시스템에서 **컨슈머 병목 현상**을 실시간 감지할 수 있다.

<br>
<br>

⚙️ 3\. 전체 코드 + 상세 주석
--------------------

```python
# %%
"""
Kafka Exporter를 활용하여 특정 컨슈머 그룹의 Lag을 모니터링하는 스크립트입니다.

TODO:
1. Prometheus API를 호출하여 특정 컨슈머 그룹의 모든 파티션 Lag 합계를 가져옵니다.
2. 일정 주기(예: 5초)마다 Lag을 출력합니다.
3. Lag 값이 특정 임계값(예: 100 이상)을 초과하면 경고 메시지를 출력합니다.
"""

import time         # 반복 실행 및 대기 시간 지연을 위한 표준 모듈
import requests     # HTTP 요청을 통해 Prometheus 메트릭에 접근하기 위한 외부 라이브러리

# %%
# 설정 값
PROMETHEUS_URL = "http://localhost:9308/metrics"  # Kafka Exporter가 Prometheus 포맷으로 메트릭을 제공하는 HTTP 엔드포인트
CONSUMER_GROUP = 'assignment-group'               # 모니터링하고자 하는 Kafka 컨슈머 그룹 이름
LAG_THRESHOLD = 100                                # 전체 lag 합이 이 수치를 초과하면 경고 출력
CHECK_INTERVAL = 5                                 # 몇 초마다 lag 상태를 체크할지 (단위: 초)

# %%
# TODO 1: Prometheus API를 호출하여 특정 컨슈머 그룹의 모든 파티션 Lag 합계를 반환하는 함수
def get_consumer_lag():
    response = requests.get(PROMETHEUS_URL)      # Prometheus에서 메트릭 데이터를 가져옴 (일반 텍스트)
    lines = response.text.split('\n')            # 텍스트 데이터를 줄 단위로 나눔
    total_lag = 0                                 # 전체 lag 값을 누적할 변수 초기화

    # 각 줄을 순회하며 해당 컨슈머 그룹에 속한 lag 정보를 찾음
    for line in lines:
        if f'kafka_consumergroup_lag{{consumergroup="{CONSUMER_GROUP}"' in line:
            lag_value = float(line.split()[-1])  # lag 값은 줄의 마지막 항목에 존재 (공백 기준 split)
            total_lag += lag_value               # lag 합산

    return total_lag                             # 최종적으로 누적된 lag 값을 반환

# %%
# 메트릭을 주기적으로 모니터링하면서 임계값 초과 시 경고 출력
while True:
    lag = get_consumer_lag()    # 현재 전체 lag 값을 가져옴
    print(f"Current Lag for {CONSUMER_GROUP}: {lag}")  # 현재 lag 상태 출력

    # TODO 2: Lag이 임계값 이상이면 경고 메시지를 출력
    if lag >= LAG_THRESHOLD:
        print("WARNING: Consumer Lag is too high!")  # 경고 메시지 출력

    # TODO 3: 설정한 주기마다 lag 상태를 다시 확인 (스크립트 일시 정지)
    time.sleep(CHECK_INTERVAL)
```

<br>
<br>

📚 4\. 추가 설명 및 실무 팁
-------------------

### ✅ Kafka Exporter가 하는 역할

Kafka Exporter는 Kafka 내부 정보를 **Prometheus 형식으로 노출**해주는 중간 브릿지 역할을 한다.  
실제로 Exporter가 제공하는 대표 메트릭은 다음과 같다:

| 메트릭 이름                            | 설명                     |
| -------------------------------------- | ------------------------ |
| `kafka_consumergroup_lag`              | 각 파티션에서의 현재 Lag |
| `kafka_topic_partition_current_offset` | 최신 메시지 오프셋       |
| `kafka_consumergroup_current_offset`   | 컨슈머가 현재 읽은 위치  |

이 중 `kafka_consumergroup_lag`은 Lag 모니터링에 있어 **핵심 메트릭**이다. Lag이란 “브로커에 적재된 메시지 중 아직 컨슈머가 읽지 않은 메시지 수”로, **메시지 병목** 혹은 **컨슈머 다운**의 신호로 간주된다.

<br>

### ⚠️ 실무에서 자주 발생하는 문제 & 예방 팁

| 실수                                 | 설명 및 해결 방법                                                                                                    |
| ------------------------------------ | -------------------------------------------------------------------------------------------------------------------- |
| ❌ Exporter 포트가 다름               | Kafka Exporter는 기본적으로 `:9308`이지만, 환경에 따라 다를 수 있음 → `docker-compose.yml`이나 시스템 설정 확인 필수 |
| ❌ Lag이 항상 0으로 나옴              | 컨슈머가 동작 중이지 않거나, 메시지를 모두 처리해서 Lag이 없음 → `input-topic`에 테스트 메시지를 보내 확인           |
| ❌ 특정 컨슈머 그룹만 필터링되지 않음 | `kafka_consumergroup_lag{consumergroup="..."}` 문자열이 정확히 일치해야 함 → 대소문자 오타 주의                      |
| ❌ 메시지가 정상인데도 경고 발생      | 오프셋 커밋이 비동기적으로 지연되면 Lag이 일시적으로 높게 측정될 수 있음 → `auto.commit.interval.ms` 설정 확인       |

<br>

### 🧠 실무 확장 방향

#### 🔔 1\. Slack, Email 연동

*   Python에서 `slack_sdk`, `smtplib` 등을 사용하여 `print()` 대신 알림 발송
    
*   예시:
    
    ```python
    if lag > 1000:
        send_slack(f"Lag이 위험 수준입니다: {lag}")
    ```
    

#### 📊 2\. 시각화 도구 연동

*   Prometheus + Grafana 조합으로 Lag, Throughput, Consumer Offsets 등을 대시보드 형태로 구성
    
*   Lag에 대한 알람 룰은 Grafana Alerting 또는 Alertmanager에서 관리
    

#### 📦 3\. Docker 환경 구성 팁

Kafka Exporter를 다음과 같이 `docker-compose`로 쉽게 띄울 수 있음:

```yaml
  kafka-exporter:
    image: danielqsj/kafka-exporter
    ports:
      - "9308:9308"
    environment:
      - KAFKA_SERVER=kafka:9092
```

<br>

### 🏁 정리: 이 실습의 핵심 가치

*   Kafka 스트리밍 시스템에서 **실시간 장애 감지와 병목 대응**을 위한 기초 인프라를 이해한 것이다.
    
*   Kafka Exporter → Prometheus → Python 모니터링 구조는 매우 단순하지만, **운영 시스템에서 가장 실용적인 감시 방법** 중 하나다.
    
*   이 개념을 확장하면 SLA 위반 탐지, 자동 스케일링, 사용자 알람 시스템 등 다양한 **운영 자동화 기능**으로 발전시킬 수 있다.
    