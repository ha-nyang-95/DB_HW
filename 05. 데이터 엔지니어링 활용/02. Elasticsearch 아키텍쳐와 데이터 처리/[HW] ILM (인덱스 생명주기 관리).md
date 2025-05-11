# ILM (인덱스 생명주기 관리)

📘 1\. 실습 주제 개요
---------------

### 🔎 실습 주제: **Elasticsearch Index Lifecycle Management (ILM) 정책 구현 및 자동 Rollover 실습**

### 📌 실습 목적

이번 실습은 Elasticsearch의 ILM(Index Lifecycle Management)을 통해 **인덱스의 생성, 전환, 삭제를 자동화하는 방법**을 학습하는 것이다.  
핫-웜-콜드-삭제 구조에서 "핫" 단계의 Rollover(전환) 조건과 "삭제" 조건을 정의하고, 문서 수 증가와 시간 경과에 따른 자동 처리를 테스트한다.

### 🎯 왜 배워야 하는가?

*   대용량 로그 시스템, 모니터링 지표, 센서 데이터 수집 시스템 등에서 인덱스는 폭발적으로 증가한다.
    
*   수동으로 인덱스를 생성하거나 삭제하는 것은 비효율적이고 위험하다.
    
*   Elasticsearch의 ILM 기능을 이용하면 데이터의 **주기적 관리와 자동화**가 가능하며, 클러스터 안정성 및 운영 효율성을 높일 수 있다.
    

<br>
<br>

🛠️ 2\. 코드 구조 및 실행 흐름 해설
------------------------

### 🧭 전체 흐름 요약

```text
1. 클러스터 설정 → 2. 기존 리소스 정리 → 3. 정책 생성 → 4. 템플릿 등록
5. 초기 인덱스 + alias 생성 → 6. 문서 삽입 → 7. rollover 발생 → 8. alias 전환 확인
```

### 주요 구성 요소

| 항목              | 설명                                                  |
| ----------------- | ----------------------------------------------------- |
| `put_lifecycle()` | 문서 수(`max_docs`) 기반 롤오버 정책 + 삭제 시점 설정 |
| `put_template()`  | 특정 index pattern에 ILM 정책과 alias 적용            |
| `create()`        | 초기 인덱스를 생성하며 alias 등록 (쓰기 가능)         |
| `es.index()`      | alias를 통해 문서 삽입                                |
| `cat.indices()`   | 실제 rollover가 일어났는지 인덱스 목록 확인           |
| `get_alias()`     | alias가 가리키는 실제 인덱스를 확인                   |

<br>
<br>

⚙️ 3\. 전체 코드 + 상세 주석
--------------------

```python
from elasticsearch import Elasticsearch
import time

# 1. Elasticsearch 연결
es = Elasticsearch("http://localhost:9200")

# 2. ILM 상태 감지 주기 설정 (10초마다)
es.cluster.put_settings(body={
    "persistent": {
        "indices.lifecycle.poll_interval": "10s"
    }
})

# 3. 기존 인덱스/템플릿 삭제 (재실습 대비 초기화)
try:
    indices = es.indices.get(index="demo-ilm-*")
    for idx in indices:
        es.indices.delete(index=idx)
        print(f"Deleted index: {idx}")
except Exception as e:
    print("삭제할 인덱스 없음 또는 오류:", e)

for template in ["demo-ilm-template", "demo-template"]:
    try:
        es.indices.delete(index=template)
        print(f"기존 템플릿 {template} 삭제 완료")
    except Exception as e:
        print(f"{template} 삭제 스킵:", e)

# 4. ILM 정책 생성: 5개 문서 이상이면 rollover, 2분 후 삭제
es.ilm.put_lifecycle(name="simple-ilm-policy", body={
    "policy": {
        "phases": {
            "hot": {
                "actions": {
                    "rollover": {
                        "max_docs": 5
                    }
                }
            },
            "delete": {
                "min_age": "2m",
                "actions": {
                    "delete": {}
                }
            }
        }
    }
}) 
print("ILM 정책 생성 완료")

# 5. 템플릿 생성: alias와 정책 연결
es.indices.put_template(name="demo-ilm-template", body={
    "index_patterns": ["demo-ilm-*"],
    "priority": 10,
    "template": {
        "settings": {
            "index.lifecycle.name": "simple-ilm-policy",
            "index.lifecycle.rollover_alias": "demo-ilm-write"
        }
    }
})  
print("템플릿 생성 완료")

# 6. 초기 인덱스 생성 + alias 연결
es.indices.create(index="demo-ilm-000001", body={
    "aliases": {
        "demo-ilm-write": {"is_write_index": True}
    }
})  
print("초기 인덱스 생성 완료")

# 7. 문서 10개 삽입 → rollover 유도
for i in range(10):
    es.index(index="demo-ilm-write", body={"msg": f"test-{i}"})
    print(f"문서 삽입: test-{i}")
    time.sleep(1)

# 8. 인덱스 상태 확인
print("\n현재 demo-ilm-* 인덱스 목록:")
print(es.cat.indices(index="demo-ilm-*", format="text"))

# 9. ILM 상태 확인
resp = es.ilm.get_lifecycle(index="demo-ilm-000001")
info = resp["indices"]["demo-ilm-000001"]
print("\nILM 상태 요약:")
print(f"인덱스: {info['index']}")
print(f"정책: {info['policy']}")
print(f"경과 시간: {info['age']}")
print(f"현재 단계: {info['phase']}")
print(f"현재 작업: {info['action']} → {info['step']}")
print(f"rollover 조건 (max_docs): {info['phase_execution']['phase_definition']['actions']['rollover']['max_docs']}")

# 10. alias가 rollover 되었는지 확인 (12초 대기)
print("\nrollover 발생 여부 확인 (12초 대기 중)...")
time.sleep(12)

try:
    alias_info = es.indices.get_alias(name="demo-ilm-write")
    print("\ndemo-ilm-write alias가 가리키는 인덱스들:")
    for index_name, value in alias_info.items():
        alias_props = value.get("aliases", {}).get("demo-ilm-write", {})
        is_write = alias_props.get("is_write_index", False)
        status = "쓰기 대상" if is_write else "읽기 전용"
        print(f" - {index_name} ({status})")
except Exception as e:
    print("alias 조회 실패:", e)
```

<br>
<br>

📚 4\. 추가 설명 및 실무 팁
-------------------

### ✅ 자주 하는 실수

| 실수                       | 해결 방법                                                      |
| -------------------------- | -------------------------------------------------------------- |
| `rollover`가 일어나지 않음 | 초기 인덱스 생성 시 `is_write_index: True` 설정 누락 여부 확인 |
| ILM이 작동하지 않음        | `poll_interval` 너무 길거나, 정책과 index alias 연결 안 됨     |
| alias로 문서 삽입 시 오류  | write index가 설정되지 않음 (특히 수동으로 alias 부여 시 주의) |

### 🚀 실무 팁

| 팁 항목                | 활용 방안                                                          |
| ---------------------- | ------------------------------------------------------------------ |
| ✅ Rollover 조건 다양화 | `max_age`, `max_size`, `max_docs` 등 복합 조건 설정 가능           |
| ✅ alias 관리           | Kibana DevTools에서 `GET _alias`로 가시성 확보                     |
| ✅ logstash 연동        | output alias 설정 후 ILM 자동 정책 연동 가능 (`index.lifecycle.*`) |
| ✅ 보관 기간 정책       | delete phase에 `min_age: "30d"`로 설정해 보존 정책 자동화          |
