# 특정 시점의 Kafka 브로커 성능 데이터를 수집 및 분석

📘 1\. 실습 주제 개요
---------------

이번 실습의 목적은 Kafka 브로커의 실시간 메시지 처리 성능을 정량적으로 수집하고, 해당 데이터를 기반으로 브로커의 **부하 상태와 처리 효율**을 분석하는 것이다.

Kafka는 고속 스트리밍 시스템이기 때문에, **브로커의 처리 속도(`MessagesInPerSec`)** 가 시스템의 핵심 성능 지표로 작용한다. Prometheus는 Kafka Exporter 혹은 JMX Exporter 등을 통해 이러한 지표들을 실시간으로 수집할 수 있으며, `/api/v1/query` 또는 `/api/v1/query_range` 같은 REST API를 통해 외부 애플리케이션에서 바로 데이터를 가져올 수 있다.

본 실습은 Python `requests` 모듈을 사용하여 Prometheus에서 `kafka_server_BrokerTopicMetrics_MessagesInPerSec` 지표를 조회하고, 이를 분석하여 브로커의 현재 상태를 진단하는 데 목적이 있다. 이는 운영 환경에서 다음과 같은 문제를 사전에 감지하거나 추적할 때 유용하다:

*   Kafka 브로커가 과부하 상태인지 판단
    
*   특정 시간 동안 메시지 유입량이 급증했는지 분석
    
*   성능 이상 징후(예: 처리량 급감)를 자동으로 감지
    

<br>
<br>

🛠️ 2\. 코드 구조 및 흐름 해설 + 실행 결과 예시 및 해설
-------------------------------------


### 🧩 전체 흐름 요약

```text
[Kafka Exporter] → [Prometheus 서버] ← [Python 스크립트: requests.get()]
                                     ↓
          kafka_server_BrokerTopicMetrics_MessagesInPerSec 지표 조회
                                     ↓
                → 메시지 처리 속도 (rate), 총 처리량 평가
```


### 🔍 코드 흐름 세부 설명

#### ✅ 설정 부분

```python
PROMETHEUS_URL = "http://localhost:9090/api/v1/query"
```

*   `localhost:9090`: Prometheus가 실행되고 있는 기본 포트
    
*   `/api/v1/query`: 단일 시점 쿼리를 위한 REST API 엔드포인트
    
*   만약 시간 구간별 변화량을 보고 싶다면 `/api/v1/query_range`를 사용해야 함
    
<br>

#### ✅ 메트릭 수집 함수

```python
def get_broker_metrics():
    response = requests.get(PROMETHEUS_URL, params={
        "query": "rate(kafka_server_BrokerTopicMetrics_MessagesInPerSec[1m])",
        "start": "now-1m",
        "end": "now"
    })
    return response.json()
```

*   `rate(...)`: Prometheus의 내장 함수로, **초당 평균 처리량**을 계산
    
*   `[1m]`: 1분 단위 윈도우를 의미. 즉, 최근 1분간의 메시지 처리 속도를 추정
    
*   `"query"` 파라미터에 PromQL을 전달하고 있음
    
*   `start`와 `end`는 **`/api/v1/query`에서는 무시됨**, 이는 사실 `query_range`용 파라미터이며 코드에서 잘못 사용된 부분
    

> ⚠️ 정리:
> 
> *   `/api/v1/query`는 시점형 쿼리이며, `"query"` 파라미터만 유효함
>     
> *   `start`, `end`는 무시되므로 의미 없는 파라미터임 → 제거 필요
>     

<br>

#### ✅ 성능 분석 함수

```python
def analyze_broker_performance():
    response = get_broker_metrics()
    print(response)
```

*   현재는 단순히 Prometheus에서 반환한 JSON 응답 전체를 `print()`만 하고 있음
    
*   실제 분석을 하려면 다음 정보들을 추출해야 함:
    
    *   각 브로커별 처리 속도 (`metric.instance` 또는 `metric.broker_id`)
        
    *   토픽별 메시지 수신 속도
        
    *   전체 처리량의 평균, 최대, 최소
        

<br>

### 🖥️ 예상 응답 JSON 구조

```json
{
  "status": "success",
  "data": {
    "resultType": "vector",
    "result": [
      {
        "metric": {
          "__name__": "kafka_server_BrokerTopicMetrics_MessagesInPerSec",
          "instance": "kafka-broker-1:7071",
          "topic": "test-topic"
        },
        "value": [1683801234.123, "452.5"]
      },
      {
        "metric": {
          "__name__": "kafka_server_BrokerTopicMetrics_MessagesInPerSec",
          "instance": "kafka-broker-2:7071",
          "topic": "test-topic"
        },
        "value": [1683801234.125, "317.9"]
      }
    ]
  }
}
```

*   `"value"[1]`은 초당 메시지 수신량 (예: `"452.5"`는 1초당 약 452개의 메시지를 수신 중)
    
*   `"metric"` 내부의 `instance`와 `topic` 정보를 기준으로 어떤 브로커가 어떤 토픽에서 얼마나 많은 메시지를 받고 있는지 파악 가능
    

<br>
<br>

⚙️ 3\. 전체 코드 + 상세 주석
--------------------

```python
# %%
"""
Kafka 브로커의 주요 성능 데이터를 수집하고 분석하는 스크립트입니다.

TODO:
1. Prometheus API를 호출하여 Kafka 브로커의 메시지 처리 속도와 총 메시지 처리량을 가져옵니다.
2. 수집된 데이터를 분석하여 Kafka 브로커의 성능을 평가합니다.
"""

import requests  # HTTP 요청을 보내기 위한 외부 라이브러리

# %%
# 설정 값
PROMETHEUS_URL = "http://localhost:9090/api/v1/query"  # Prometheus의 단일 시점 쿼리 엔드포인트

# %%
# TODO 1: Prometheus API를 호출하여 Kafka 브로커의 메시지 처리 속도와 총 메시지 처리량을 가져오는 함수
def get_broker_metrics():
    # PromQL을 통해 최근 1분간 Kafka 메시지 수신 속도(rate)를 초당 기준으로 가져온다
    query = "rate(kafka_server_BrokerTopicMetrics_MessagesInPerSec[1m])"
    
    # HTTP GET 요청으로 Prometheus API를 호출
    response = requests.get(PROMETHEUS_URL, params={"query": query})
    
    # 응답을 JSON 형식으로 변환하여 반환
    return response.json()

# %%
# TODO 2: 수집된 데이터를 기반으로 Kafka 브로커의 성능을 평가하는 함수
def analyze_broker_performance():
    # Prometheus로부터 지표 응답을 가져옴
    data = get_broker_metrics()

    # 결과 리스트 추출
    results = data.get("data", {}).get("result", [])
    
    if not results:
        print("❗ 브로커 성능 데이터가 없습니다.")
        return

    print("📊 Kafka 브로커 성능 요약 (MessagesInPerSec):")
    print("────────────────────────────────────────────")
    
    total_rate = 0.0  # 전체 브로커 처리량 누적 변수
    count = 0         # 브로커 수 카운트

    for item in results:
        metric = item.get("metric", {})
        value = item.get("value", [])[1]  # ["timestamp", "value"]
        
        topic = metric.get("topic", "N/A")
        instance = metric.get("instance", "unknown")

        rate = float(value)
        total_rate += rate
        count += 1

        print(f"📦 브로커 인스턴스: {instance} | 토픽: {topic} | 처리 속도: {rate:.2f} msg/sec")
    
    print("────────────────────────────────────────────")
    print(f"✅ 총 브로커 수: {count}")
    print(f"✅ 전체 메시지 처리량 (합): {total_rate:.2f} msg/sec")
    print(f"✅ 평균 처리 속도 (브로커당): {total_rate / count:.2f} msg/sec")

# %%
# 성능 분석 함수 실행
analyze_broker_performance()
```

<br>
<br>

📚 4\. 추가 설명 및 실무 팁
-------------------

### ✅ 실무에서 MessagesInPerSec 지표가 중요한 이유

Kafka 브로커에서 `"kafka_server_BrokerTopicMetrics_MessagesInPerSec"`는 다음과 같은 판단의 기준이 된다:

| 목적 | 설명 |
| --- | --- |
| 병목 탐지 | 메시지 유입량에 비해 Consumer Lag이 계속 쌓이면, Consumer 처리 병목 |
| 토픽 이상 감지 | 특정 토픽의 처리량이 급변하면 서비스 사용 패턴 또는 장애 가능성 탐지 |
| 수요 예측 | 시간대별 처리량 패턴으로 트래픽 예측 가능 |
| 오토스케일링 기준 | Kafka 클러스터의 autoscaling을 위한 메트릭으로 활용 가능 |

* * *

### 🧨 실무에서 자주 마주치는 문제들

| 문제 | 원인 및 대응 방법 |
| --- | --- |
| ❌ 데이터가 없음 | Prometheus 설정에 Kafka Exporter가 누락되어 있거나, Exporter가 죽어 있음 |
| ❌ 처리량이 0인데 메시지는 오고 있음 | Kafka Exporter에 JMX가 제대로 연결되지 않음 → JVM 내 exporter agent 확인 |
| ❌ 특정 브로커만 과도한 처리량 | Partition 분산이 균등하지 않거나 특정 토픽이 몰려 있음 → rebalance 필요 |
| ❌ API 호출 시 `value`가 문자열 | Prometheus의 모든 수치 데이터는 문자열로 반환됨 → `float()` 처리 필수 |

* * *

### 🧠 실무 확장 방향

#### 1\. 슬랙/이메일/웹훅 경고 자동화

*   메시지 처리 속도가 특정 기준 이하로 떨어지면 알람 전송
    
*   예시 조건: 평균 처리량이 100msg/sec 이하 → 슬랙 경고 발송
    

```python
if total_rate / count < 100:
    send_slack_alert("⚠️ Kafka 처리 속도 저하 감지!")
```

#### 2\. `query_range` API 사용으로 시간대별 변화 분석

*   처리량 추세를 시간 단위로 보고 싶을 경우, `/api/v1/query_range` 사용
    
*   예: 지난 10분간 처리량 변화 추이를 그래프로 출력
    

#### 3\. 토픽별 트래픽 정밀 분석

*   `by (topic)` 또는 `by (instance, topic)`으로 그룹화해서  
    특정 토픽에 트래픽이 집중되는지, 특정 브로커에 편향되는지 진단 가능
    

#### 4\. 성능 기준 대시보드 구축

*   `MessagesInPerSec`, `BytesInPerSec`, `BytesOutPerSec`, `RequestHandlerAvgIdlePercent`, `UnderReplicatedPartitions` 등 다양한 지표를 함께 조합해 **종합 대시보드** 구성
    
*   Prometheus + Grafana를 연동하면, 위와 같은 성능 분석이 시각적으로 실시간 확인 가능
    

* * *

### ✅ 정리: 이 실습이 갖는 실제적 가치

*   이 스크립트는 단순한 실습을 넘어 Kafka 클러스터의 **헬스 체크 기반을 자동화**한 도구다.
    
*   Python으로 Prometheus를 호출하고 응답을 파싱함으로써, 시각화 도구 없이도 **운영 상태를 코드로 점검**할 수 있다.
    
*   위에서 다룬 지표들을 토대로, 향후 자동 리밸런싱, 장애 탐지, 리포트 자동화 등 다양한 활용 가능성이 열려 있다.
    

* * *

이렇게 실습 전체를 네가 요청한 네 가지 항목에 맞춰 정리 완료했어.  
혹시 이 스크립트를 바탕으로 더 확장하거나, 여러 개의 Kafka 모니터링 지표를 통합하는 실습으로 나아가고 싶다면 이어서 도와줄게.

다음으로 어떤 내용을 이어서 정리해볼까?



---
Powered by [ChatGPT Exporter](https://www.chatgptexporter.com)