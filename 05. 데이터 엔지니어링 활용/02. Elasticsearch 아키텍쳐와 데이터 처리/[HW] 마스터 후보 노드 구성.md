# 마스터 후보 노드 구성

📘 1\. 실습 주제 개요
---------------

### 🔎 실습 주제: **Elasticsearch 마스터 노드 장애 복구 및 재합류 시뮬레이션**

### 📌 실습 목적

이 실습은 Elasticsearch 클러스터의 고가용성(High Availability, HA)을 보장하기 위해 **마스터 노드 장애에 대한 자동 대처 능력과 클러스터 복원력**을 이해하고 직접 확인하는 것이 목적이다.

운영 환경에서는 마스터 노드가 예기치 않게 종료되거나 네트워크에서 격리되는 경우가 발생할 수 있다. 이 때, Elasticsearch는 **다른 노드들 중 하나를 자동으로 새로운 마스터 노드로 선출**하여 클러스터 상태를 유지한다.

### 🎯 왜 이걸 배우는가?

*   Elasticsearch는 분산 시스템이며, 마스터 노드가 클러스터 메타데이터(인덱스 설정, 샤드 위치 등)를 관리한다.
    
*   장애가 발생해도 시스템이 지속적으로 작동하려면 마스터 노드가 자동으로 재선출되어야 한다.
    
*   실무에서는 시스템 로그 이상, 네트워크 장애, 컨테이너 다운 등 다양한 상황에서 이러한 로직이 실제로 잘 작동하는지 확인해야 한다.
    

<br>
<br>

🛠️ 2\. 코드 구조 및 실행 흐름 해설
------------------------

### 🧭 전체 흐름 요약

```text
1. 연결된 클러스터 노드 확인
2. 현재 마스터 노드 확인
3. 마스터 노드 컨테이너 중지 (장애 시뮬레이션)
4. 나머지 노드로 재연결 및 마스터 재선출 확인
5. 중지된 노드 재시작 및 클러스터 재합류 확인
```

### 🔍 핵심 단계 해설

| 단계                            | 설명                                                                           |
| ------------------------------- | ------------------------------------------------------------------------------ |
| **Elasticsearch 연결**          | `Elasticsearch("http://localhost:9200")`로 초기 클라이언트 연결                |
| **현재 노드 상태 확인**         | `es.cat.nodes(format="json")` → 클러스터에 연결된 모든 노드와 역할 조회        |
| **마스터 노드 식별**            | `es.cat.master(format="json")` → 현재 마스터 노드 정보 출력                    |
| **Docker 컨테이너 중지**        | `subprocess.run(["docker", "stop", master_node_name])`를 통해 마스터 노드 종료 |
| **남은 노드 재연결**            | `ping()` 가능한 노드를 찾아 재접속 → 마스터 재선출이 일어남                    |
| **5초 대기 → 마스터 변경 확인** | 클러스터 안정화 대기 후 새로운 마스터 확인                                     |
| **중지된 노드 재시작 및 감시**  | 재시작 후 최대 30초간 합류 여부 반복 체크                                      |
| **최종 상태 출력**              | 모든 노드와 새 마스터 상태 출력                                                |

<br>
<br>

⚙️ 3\. 전체 코드 + 상세 주석
--------------------

```python
from elasticsearch import Elasticsearch
import subprocess
import time

# 1. 가능 노드 리스트에서 재연결
def reconnect_to_alive_node(possible_hosts):
    for host in possible_hosts:
        try:
            es = Elasticsearch(host)
            if es.ping():
                print(f"{host} 연결 성공")
                return es
        except Exception:
            continue
    raise Exception("사용 가능한 Elasticsearch 노드가 없습니다.")

# 2. 초기 연결
es = Elasticsearch("http://localhost:9200")

# 3. 노드 상태 확인
print("현재 노드 상태:")
nodes_info = es.cat.nodes(format="json")
for node in nodes_info:
    print(f" - 이름: {node['name']}, 역할: {node['node.role']}, IP: {node['ip']}")

# 4. 마스터 노드 확인
print("\n현재 마스터 노드:")
master = es.cat.master(format="json")[0]
master_node_name = master['node']
print(f" - 마스터 노드: {master_node_name}, IP: {master['ip']}")

# 5. 마스터 노드 중단
print(f"\n마스터 노드 '{master_node_name}' 컨테이너 중지")
subprocess.run(["docker", "stop", master_node_name], check=True)

# 6. 재연결 시도
print("\n남은 노드로 재연결 시도 중...")
remaining_hosts = [
    "http://localhost:9200",
    "http://localhost:9201",
    "http://localhost:9202"
]
# 중단된 IP 제외
remaining_hosts = [host for host in remaining_hosts if not host.endswith(master['ip'].split('.')[-1])]
es = reconnect_to_alive_node(remaining_hosts)

# 7. 클러스터 안정화 대기
time.sleep(5)
print("\n마스터 노드 중지 후 노드 상태:")
nodes_info = es.cat.nodes(format="json")
for node in nodes_info:
    print(f" - 이름: {node['name']}, 역할: {node['node.role']}, IP: {node['ip']}")

# 8. 새 마스터 확인
print("\n새 마스터 노드 확인:")
new_master = es.cat.master(format="json")[0]
print(f" - 새 마스터 노드: {new_master['node']}, IP: {new_master['ip']}")

# 9. 중지 노드 재시작
print(f"\n중지된 마스터 노드 '{master_node_name}' 재시작")
subprocess.run(["docker", "start", master_node_name], check=True)

# 10. 클러스터 재합류 감시
print(f"\n'{master_node_name}' 노드 재합류 대기 중...")
for i in range(30):
    nodes_info = es.cat.nodes(format="json")
    node_names = [node["name"] for node in nodes_info]
    if master_node_name in node_names:
        print(f"{master_node_name} 노드 클러스터에 재합류 완료")
        break
    time.sleep(1)
else:
    print(f"30초 내에 {master_node_name} 노드가 클러스터에 합류하지 못했습니다.")

# 11. 최종 상태 출력
print("\n최종 클러스터 노드 상태:")
nodes_info = es.cat.nodes(format="json")
for node in nodes_info:
    print(f" - 이름: {node['name']}, 역할: {node['node.role']}, IP: {node['ip']}")

print("\n최종 마스터 노드:")
final_master = es.cat.master(format="json")[0]
print(f" - 마스터 노드: {final_master['node']}, IP: {final_master['ip']}")
```

<br>
<br>

📚 4\. 추가 설명 및 실무 팁
-------------------

### ⚠️ 실무에서 마주칠 수 있는 상황

| 문제 상황                         | 실무 대응 방법                                                   |
| --------------------------------- | ---------------------------------------------------------------- |
| 마스터 노드 종료 시 클러스터 다운 | `minimum_master_nodes` 설정 누락 시 발생 가능 → quorum 보장 필수 |
| 재시작 후 노드 합류 실패          | IP 충돌, Docker 네트워크 설정 문제, 데이터 디렉토리 손상 등 점검 |
| 클러스터 분할(brain split)        | 동일 cluster.name 사용, 적절한 discovery 설정 필요               |

### 🚀 심화 학습 방향

*    `discovery.seed_hosts`, `cluster.initial_master_nodes` 설정 방식 차이 분석
    
*    `voting_only` 노드 역할 구성 실습
    
*    `cluster.routing.allocation.*` 정책으로 샤드 재배치 제어
    
*    `Kibana`나 `GET _cat/health?v`로 상태 시각화
    
