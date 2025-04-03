# Kafka 모니터링 설정

* * *

🧠 Kafka + Prometheus + Python + Exporter + JMX + Grafana 통합 실습 완전 정리
=====================================================================

🎯 실습 목적
--------

*   Kafka에서 **Consumer Group의 지연(Lag)** 을 실시간으로 확인
    
*   Prometheus를 통해 **지표 수집 및 저장**
    
*   Grafana로 **데이터 시각화**
    
*   Python으로 **지연 상황 경고 모니터링**
    
*   Kafka 내부 JVM 메트릭도 JMX Exporter로 수집
    

* * *

📦 실습 환경
--------

| 구성 요소 | 역할 |
| --- | --- |
| Kafka | 메시지 시스템 |
| Zookeeper | Kafka 클러스터 관리 |
| Kafka Exporter | Kafka consumer lag 수집 |
| Prometheus | 지표 수집 및 저장 |
| Python | 지표 조회 및 경고 |
| JMX Exporter | Kafka JVM 메트릭 수집 |
| Grafana | 시각화 도구 |

* * *

✅ 설치 및 실행 순서 요약 (필요한 터미널: 5~6개)
-------------------------------

| 터미널 번호 | 역할 | 폴더 위치 |
| --- | --- | --- |
| 1 | Zookeeper 실행 | `/usr/local/kafka` |
| 2 | Kafka 실행 (JMX Exporter 연동 포함) | `/usr/local/kafka` |
| 3 | Kafka Exporter 실행 | `~/kafka_exporter-1.4.2.linux-amd64` |
| 4 | Prometheus 실행 | `~/prometheus-2.47.2.linux-amd64` |
| 5 | Python 모니터링 코드 실행 | `~/KAFKA-PYTHON-TEST` |
| 6 (선택) | Grafana 실행 | `~/grafana-10.2.2` |

* * *

🪜 Step-by-Step 전체 정리
---------------------

* * *

### ✅ \[1\] Zookeeper 실행

```bash
cd /usr/local/kafka
bin/zookeeper-server-start.sh config/zookeeper.properties
```

* * *

### ✅ \[2\] JMX Exporter 연동한 Kafka 실행

#### 2-1. JAR 다운로드

```bash
cd /usr/local/kafka
wget https://repo1.maven.org/maven2/io/prometheus/jmx/jmx_prometheus_javaagent/0.17.2/jmx_prometheus_javaagent-0.17.2.jar
```

#### 2-2. 설정 파일 작성

```bash
nano config.yaml
```

```yaml
lowercaseOutputName: true
lowercaseOutputLabelNames: true
rules:
  - pattern: ".*"
```

#### 2-3. Kafka 실행 (JMX 연동 포함)

```bash
export KAFKA_OPTS="-javaagent:/usr/local/kafka/jmx_prometheus_javaagent-0.17.2.jar=9094:/usr/local/kafka/config.yaml"
bin/kafka-server-start.sh config/server.properties
```

> 🧠 같은 터미널 내에서 export와 실행을 같이 해야 유효합니다!

* * *

### ✅ \[3\] Kafka Exporter 실행

```bash
cd ~/kafka_exporter-1.4.2.linux-amd64
chmod +x kafka_exporter
./kafka_exporter --kafka.server=localhost:9092
```

* * *

### ✅ \[4\] Prometheus 설정 및 실행

#### 4-1. 설정 파일 수정

```bash
cd ~/prometheus-2.47.2.linux-amd64
nano prometheus.yml
```

```yaml
global:
  scrape_interval: 5s

scrape_configs:
  - job_name: 'kafka'
    static_configs:
      - targets: ['localhost:9094']  # JMX Exporter (Kafka JVM 정보)

  - job_name: 'kafka_exporter'
    static_configs:
      - targets: ['localhost:9308']  # Kafka Exporter (Consumer Lag)
```

#### 4-2. 실행

```bash
./prometheus --config.file=prometheus.yml
```

> 확인: [http://localhost:9090](http://localhost:9090)

* * *

### ✅ \[5\] Kafka topic + consumer group 생성 (테스트용)

```bash
# 토픽 생성
bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --topic test-topic --partitions 1 --replication-factor 1

# producer 실행
bin/kafka-console-producer.sh --broker-list localhost:9092 --topic test-topic
> hello
> world

# consumer 실행
bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic test-topic --group assignment-group
```

* * *

### ✅ \[6\] Python 코드 작성 및 실행

#### 6-1. skeleton.py 작성

```python
import time
import requests

PROMETHEUS_URL = "http://localhost:9308/metrics"
CONSUMER_GROUP = "assignment-group"
LAG_THRESHOLD = 100
CHECK_INTERVAL = 5

def get_consumer_lag():
    response = requests.get(PROMETHEUS_URL)
    lines = response.text.split('\n')
    total_lag = 0
    for line in lines:
        if f'kafka_consumergroup_lag{{consumergroup="{CONSUMER_GROUP}"' in line:
            lag_value = float(line.split()[-1])
            total_lag += lag_value
    return total_lag

while True:
    lag = get_consumer_lag()
    print(f"Current Lag for {CONSUMER_GROUP}: {lag}")
    if lag > LAG_THRESHOLD:
        print("WARNING: Consumer Lag is too high!")
    time.sleep(CHECK_INTERVAL)
```

#### 6-2. 실행

```bash
cd ~/KAFKA-PYTHON-TEST
source venv/bin/activate
python skeleton.py
```

* * *

### ✅ \[7\] Grafana 설치 및 대시보드 구성 (선택)

#### 7-1. 설치 및 실행

```bash
cd ~
wget https://dl.grafana.com/oss/release/grafana-10.2.2.linux-amd64.tar.gz
tar -xvzf grafana-10.2.2.linux-amd64.tar.gz
cd grafana-10.2.2
./bin/grafana-server
```

> 접속: [http://localhost:3000](http://localhost:3000)  
> 로그인: **admin / admin**

#### 7-2. 데이터 소스 설정

1.  좌측 메뉴 > Data Sources > Add data source
    
2.  Prometheus 선택
    
3.  URL에 `http://localhost:9090`
    
4.  Save & Test
    

#### 7-3. 대시보드 추가

*   [https://grafana.com/grafana/dashboards/](https://grafana.com/grafana/dashboards/) 접속
    
*   Kafka 또는 JVM 관련 대시보드 검색 후 Import
    
*   Prometheus 데이터 소스 선택
    

* * *

✅ 실습 결과 예시
----------

*   Kafka 메시지를 보내고 consumer가 읽음
    
*   Prometheus가 lag 수집 중
    
*   Python이 실시간으로 지연 출력 중  
    → `Current Lag for assignment-group: 2.0 → 0.0`
    
*   Grafana에서 지표 시각화 성공
    

* * *

📌 핵심 용어 요약 (비전공자용)
-------------------

| 용어 | 설명 |
| --- | --- |
| Kafka | 메시지를 토픽 단위로 주고받는 시스템 |
| Zookeeper | Kafka를 돕는 관리자 역할 |
| Topic | 메시지가 저장되는 채널 |
| Consumer Group | 메시지를 소비하는 프로그램 그룹 |
| Lag | 아직 처리되지 않고 남아있는 메시지 수 |
| Kafka Exporter | Kafka 상태를 Prometheus에 알려주는 중간 역할 |
| JMX Exporter | Kafka 내부 JVM 상태를 Prometheus에 알려주는 도구 |
| Prometheus | 지표 데이터를 수집하고 저장 |
| Grafana | 데이터를 시각화하는 도구 |
| Python | Prometheus에서 lag을 가져와 모니터링하는 코드 작성용 언어 |

* * *

🎉 마무리
------

축하합니다!  
이 실습을 통해 **Kafka 시스템을 전반적으로 이해하고, 지표 수집 → 경고 모니터링 → 시각화**까지 완전한 모니터링 환경을 직접 구축하셨습니다.

> 💡 다음에 배우면 좋은 것들:

*   Docker로 이 환경 통합 구성하기
    
*   Alertmanager로 슬랙/메일 알림 설정
    
*   Kafka에 직접 consumer 앱 만들어 보기 (Python, Java 등)
    
