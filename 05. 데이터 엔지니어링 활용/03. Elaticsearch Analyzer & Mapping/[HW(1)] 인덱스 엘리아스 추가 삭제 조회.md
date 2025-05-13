# 인덱스 엘리아스 추가 삭제 조회

📘 1. 실습 주제 개요
--------------

### 🧩 주제: Elasticsearch 인덱스 및 앨리어스(Alias) 관리 실습

<br>

### 🔍 왜 배우는가?

현대의 데이터 시스템에서는 실시간 로그, 사용자 이벤트, 서비스 상태 정보 등 다양한 형태의 데이터를 빠르게 수집하고 분석해야 합니다. 이때 **Elasticsearch**는 이런 데이터를 빠르게 저장하고 검색하는 데 특화된 도구입니다.

하지만 데이터를 효율적으로 운영하기 위해서는 **단순 저장**만이 아니라, 데이터를 **유지보수 가능한 구조로 관리**하는 것이 중요합니다. 그 핵심 기능 중 하나가 **인덱스(Index)** 와 **앨리어스(Alias)** 입니다.

<br>

### 🎯 학습 목표

이번 실습에서는 다음과 같은 Elasticsearch의 핵심 관리 기능을 직접 수행해 봅니다.

1.  **인덱스 생성과 삭제**: 데이터를 저장할 공간을 만들고 지우는 법
    
2.  **앨리어스 추가와 제거**: 실제 인덱스 이름을 숨기고 별칭(Alias)으로 접근하는 기술
    
3.  **앨리어스를 통해 인덱스 찾기**: 운영환경에서 인덱스 이름을 고정하지 않고도 데이터 접근이 가능해지는 원리
    
4.  **Alias의 유용성 체험**: 인덱스 롤오버, 다중 인덱스 매핑 등 실무에서 자주 쓰이는 패턴 이해
    

<br>

### 🧠 비유를 통한 이해

> 인덱스는 책의 한 권이고, 앨리어스는 책에 붙인 '포스트잇'이라고 생각하면 이해가 쉽습니다.  
> 책(인덱스)은 여러 권이 생기고 없어질 수 있지만, 포스트잇(앨리어스)은 언제든 옮겨 붙일 수 있어서 사람들은 항상 같은 이름으로 원하는 내용을 찾을 수 있습니다.

<br>

### 🧪 실습을 통해 얻는 효과

*   시스템 운영에서 **무중단 인덱스 교체 전략**을 이해할 수 있게 됩니다.
    
*   **다수의 인덱스를 효율적으로 관리**하고, 사용자 또는 서비스가 인덱스 구조 변경을 의식하지 않아도 되게 만드는 방법을 익힐 수 있습니다.
    
*   실무에서 **Elasticsearch를 로그 관리 플랫폼**으로 활용할 때 기본기가 됩니다 (예: ELK Stack, OpenSearch, Kibana 연동 등).
    

<br>
<br>

🛠️ 2. 코드 구조 및 흐름 해설 + 실행 결과 예시
-------------------------------

### 🔄 전체 흐름 요약

이 코드는 **Elasticsearch의 인덱스와 앨리어스(alias)** 를 **순차적으로 생성, 연결, 조회, 삭제**하는 작업을 자동화한 스크립트입니다. 흐름은 다음과 같이 진행됩니다:

1.  기존 인덱스 삭제
    
2.  새로운 인덱스 생성
    
3.  앨리어스(alias) 부여
    
4.  현재 존재하는 앨리어스 조회
    
5.  앨리어스 → 인덱스 매핑 확인
    
6.  앨리어스 삭제
    
7.  삭제 후 앨리어스 확인
    

<br>

### 💡 주요 구성 및 해설

#### ✅ 1단계: 기존 인덱스 삭제

```python
if es.indices.exists(index=index_name):
    es.indices.delete(index=index_name)
```

*   Elasticsearch에 동일한 이름(`logs-000001`)의 인덱스가 이미 있을 경우 삭제합니다.
    
*   삭제하지 않으면 중복 오류가 발생할 수 있기 때문에 **사전 정리 단계**입니다.
    

📌 실행 예시:

```
기존 인덱스 [logs-000001] 삭제 완료
```

<br>

#### ✅ 2단계: 새로운 인덱스 생성

```python
es.indices.create(index=index_name, body={"settings": {"number_of_replicas": 0}})
```

*   복제본 없이 인덱스를 생성합니다. 복제본은 고가용성을 위한 백업 사본인데, 실습 목적이므로 `0`으로 설정했습니다.
    
*   `number_of_shards`는 기본값(5)을 사용합니다.
    

📌 실행 예시:

```
인덱스 [logs-000001] 생성 완료
```

<br>

#### ✅ 3단계: 앨리어스 연결

```python
es.indices.update_aliases(body={"actions": [{"add": {"alias": alias_name, "index": index_name}}]})
```

*   `logs-alias`라는 별칭을 `logs-000001` 인덱스에 부여합니다.
    
*   실무에서는 이 alias 이름을 통해 서비스가 인덱스에 접근하게 하여 **무중단 인덱스 전환**이 가능해집니다.
    

📌 실행 예시:

```
앨리어스 [logs-alias] 추가 완료
```

<br>

#### ✅ 4단계: 현재 앨리어스 전체 조회

```python
aliases = es.cat.aliases(format="json")
```

*   모든 앨리어스 목록을 JSON 형태로 가져온 뒤, `"logs-"`로 시작하는 것만 출력합니다.
    
*   이때 `cat` API는 사람이 보기 쉬운 요약 정보를 반환하는 경량 조회 명령입니다.
    

📌 실행 예시:

```
logs-alias                                 logs-000001
```

<br>

#### ✅ 5단계: 특정 alias → 인덱스 매핑 조회

```python
alias_info = es.indices.get_alias(name=alias_name)
```

*   `logs-alias`라는 alias가 어떤 인덱스를 가리키고 있는지 확인합니다.
    

📌 실행 예시:

```
logs-alias → logs-000001
```

<br>

#### ✅ 6단계: 앨리어스 제거

```python
es.indices.update_aliases(body={"actions": [{"remove": {"alias": alias_name, "index": index_name}}]})
```

*   해당 인덱스로부터 alias를 제거합니다. 인덱스 자체는 그대로 존재하지만, 별칭은 사라집니다.
    

📌 실행 예시:

```
앨리어스 [logs-alias] 삭제 완료
```

<br>

#### ✅ 7단계: 앨리어스 삭제 확인

```python
aliases_after = es.cat.aliases(format="json")
```

*   삭제 이후 앨리어스 목록에서 `logs-alias`가 사라졌는지 확인합니다.
    

📌 실행 예시:

```
(출력 없음) → logs-alias가 존재하지 않음
```

<br>
<br>

⚙️ 3. 전체 코드 + 상세 주석
-------------------

```python
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
import time

# ----------------------------------------------
# Elasticsearch 클라이언트 연결
# ----------------------------------------------
es = Elasticsearch("http://localhost:9200")  # 로컬 호스트에 실행 중인 ES 클러스터에 연결

index_name = "logs-000001"  # 생성/삭제할 인덱스 이름
alias_name = "logs-alias"   # 인덱스에 연결할 별칭(Alias)

# ----------------------------------------------
# 1. 기존 인덱스 삭제
# ----------------------------------------------
print("기존 인덱스 확인 및 삭제")
if es.indices.exists(index=index_name):
    es.indices.delete(index=index_name)  # 이미 존재하는 인덱스 삭제
    print(f"기존 인덱스 [{index_name}] 삭제 완료")
else:
    print(f"기존 인덱스 [{index_name}] 없음. 새로 생성 진행.")
print()
time.sleep(1)

# ----------------------------------------------
# 2. 인덱스 생성
# ----------------------------------------------
print(f"인덱스 [{index_name}] 생성")
# 복제본(replica)을 0으로 설정하여 불필요한 리소스 낭비 방지 (단일 노드 환경 가정)
es.indices.create(index=index_name, body={
    "settings": {
        "number_of_replicas": 0
    }
})
print(f"인덱스 [{index_name}] 생성 완료")
time.sleep(1)

# ----------------------------------------------
# 3. 앨리어스 추가
# ----------------------------------------------
print(f"앨리어스 [{alias_name}] 추가 → 인덱스 [{index_name}]")
# update_aliases API를 통해 alias 이름을 인덱스에 매핑
es.indices.update_aliases(body={
    "actions": [
        {"add": {"alias": alias_name, "index": index_name}}
    ]
})
print(f"앨리어스 [{alias_name}] 추가 완료")
print()
time.sleep(1)

# ----------------------------------------------
# 4. 현재 모든 앨리어스 조회
# ----------------------------------------------
print("logs-* 패턴에 해당하는 앨리어스만 조회")
# cat.aliases: 사람이 읽기 쉬운 요약 정보를 반환하는 경량 API
aliases = es.cat.aliases(format="json")
for alias in aliases:
    if alias["alias"].startswith("logs-"):  # logs-로 시작하는 alias만 출력
        print(f'{alias["alias"]:<45} {alias["index"]}')
print()
time.sleep(1)

# ----------------------------------------------
# 5. 특정 앨리어스로 인덱스 조회
# ----------------------------------------------
print("앨리어스를 이용하여 해당하는 인덱스 찾기")
try:
    alias_info = es.indices.get_alias(name=alias_name)
    for idx in alias_info:
        print(f"{alias_name} → {idx}")
except NotFoundError:
    print(f"앨리어스 [{alias_name}]를 찾을 수 없습니다.")
print()
time.sleep(1)

# ----------------------------------------------
# 6. 앨리어스 삭제
# ----------------------------------------------
print(f"앨리어스 [{alias_name}] 삭제 → 인덱스 [{index_name}]")
# 기존에 연결된 alias를 제거하는 작업
es.indices.update_aliases(body={
    "actions": [
        {"remove": {"alias": alias_name, "index": index_name}}
    ]
})
print(f"앨리어스 [{alias_name}] 삭제 완료")
print()
time.sleep(1)

# ----------------------------------------------
# 7. 삭제 후 앨리어스 다시 조회
# ----------------------------------------------
print("앨리어스 삭제 후 조회")
aliases_after = es.cat.aliases(format="json")
for alias in aliases_after:
    if alias["alias"].startswith("logs-"):
        print(f'{alias["alias"]:<45} {alias["index"]}')
print()

print("인덱스 및 앨리어스 관리 작업 완료")
```

<br>
<br>

📚 4. 추가 설명 및 실무 팁
------------------

### 🔧 실무에서 Alias를 사용하는 이유

**Alias(앨리어스)** 는 실제 인덱스의 이름을 감추고, 고정된 이름으로 인덱스에 접근할 수 있도록 도와주는 "가상 인덱스 이름"입니다.

#### 💡 주요 활용 예:

1.  **무중단 인덱스 교체**
    
    *   `logs-000001` → `logs-000002`로 교체할 때, 실제 서비스는 `logs-alias`만 바라보기 때문에 중단 없이 새로운 인덱스를 사용할 수 있음.
        
2.  **읽기/쓰기 분리**
    
    *   하나의 인덱스에 `read-alias`, `write-alias`를 분리하여 설정 가능.
        
3.  **보안 정책 적용**
    
    *   특정 사용자는 특정 alias만 접근 가능하게 설정하여 데이터 접근을 통제.
        

<br>

### 🧱 자주 하는 실수 및 주의점

| 실수/이슈                          | 설명                                                                               |
| ---------------------------------- | ---------------------------------------------------------------------------------- |
| ✅ alias 삭제 후 인덱스 삭제 누락   | alias만 삭제하고 인덱스를 방치하면 불필요한 저장소 사용 지속                       |
| ✅ alias 중복 연결                  | 동일 alias를 여러 인덱스에 연결하면 의도치 않게 검색 결과가 분산됨                 |
| ✅ alias 제거 없이 신규 인덱스 생성 | 기존 alias를 제거하지 않으면 충돌이 발생하거나 이전 인덱스를 여전히 바라볼 수 있음 |
| ✅ number\_of\_replicas 미설정      | 단일 노드 테스트 환경에서는 replica를 0으로 설정해야 성능 저하 방지                |

<br>

### 🔬 심화 학습 방향

#### 📌 Index Lifecycle Management (ILM)

*   실무에서는 **인덱스를 자동으로 생성/전환/삭제**해야 할 경우가 많습니다.
    
*   ILM은 "hot → warm → cold → delete" 같은 단계로 인덱스 수명 주기를 정의할 수 있게 해줍니다.
    

#### 📌 Rollover API

*   일정 문서 수 혹은 기간을 기준으로 새 인덱스로 전환하는 기능.
    
*   alias를 고정한 채 인덱스를 자동 교체 가능 → 실시간 로그 시스템에 적합.
    

#### 📌 Kibana로 alias 시각화

*   Kibana를 활용하면 인덱스와 alias의 관계를 시각적으로 확인할 수 있어, 운영자가 쉽게 구조를 파악 가능.
    

<br>

### 🧠 마무리 정리

이번 실습은 Elasticsearch 인덱스 관리의 가장 기초적이고 중요한 단계를 다루었습니다.  
실제 운영 환경에서는 수십~수백 개의 인덱스가 생성되고, 데이터 유지 기간이나 검색 속도 최적화를 위해 **alias를 전략적으로 운용**하는 것이 필수입니다.

따라서 오늘 실습한 코드는 단순한 테스트 스크립트가 아니라, **실무에서도 충분히 활용 가능한 기초 운영 템플릿**이라고 할 수 있습니다.

