# python을 통한 이커머스 데이터 Elasticsearch Document API

📘 1\. 실습 주제 개요
---------------

### 🔎 실습 주제: Elasticsearch의 문서 CRUD 및 Upsert 기능 구현

### 📌 실습 목적

Elasticsearch에서 가장 기본적이고 중요한 문서 조작 기능(CRUD)을 익히고, `Upsert`처럼 실무에 활용도가 높은 기능의 동작 원리를 파악한다.  
이를 통해 RESTful 구조의 데이터 저장 방식과 JSON 기반 검색/수정 작업에 익숙해지며, NoSQL 시스템에 대한 이해도를 높인다.

### 🎯 학습 배경 및 필요성

*   REST API 또는 데이터 수집 파이프라인에서 문서를 동적으로 갱신하거나 새로 삽입하는 작업은 매우 빈번하다.
    
*   관계형 DB에서는 `INSERT ... ON DUPLICATE KEY UPDATE`와 유사한 방식이지만, Elasticsearch는 JSON 문서 기반으로 `index`, `update`, `get`, `delete` 등 각 동작을 별도로 제공한다.
    
*   실제 서비스에서는 상태 저장, 로그 기록, 사용자 행동 분석 등에 이 기능들이 폭넓게 사용된다.
    

<br>
<br>

🛠️ 2\. 코드 구조 및 실행 흐름 해설
------------------------

### ✅ 주요 함수 구성 요약

| 함수 이름            | 설명                                            |
| -------------------- | ----------------------------------------------- |
| `create_es_client()` | Elasticsearch 클라이언트를 생성하여 서버에 연결 |
| `create_index()`     | 인덱스 존재 여부를 확인하고, 없으면 생성        |
| `insert_document()`  | 특정 ID를 가진 문서를 삽입                      |
| `get_document()`     | 문서 ID로 문서를 조회                           |
| `update_document()`  | 문서의 특정 필드를 부분 수정                    |
| `upsert_document()`  | 문서가 없으면 삽입, 있으면 수정 (upsert)        |
| `delete_document()`  | 문서를 삭제                                     |

### ⚙️ 실행 흐름 요약 (메인 함수 기준)

1.  인덱스가 없다면 새로 생성
    
2.  ID가 1인 문서를 삽입
    
3.  문서 존재 여부 및 내용 확인
    
4.  가격 필드를 업데이트
    
5.  다시 문서 조회하여 수정 확인
    
6.  동일 문서에 대해 upsert 실행 (있으면 수정)
    
7.  삭제 및 재삽입(upsert) 흐름까지 반복 실습
    

<br>
<br>

⚙️ 3\. 전체 코드 + 상세 주석
--------------------

```python
from elasticsearch import Elasticsearch, NotFoundError

# 1. Elasticsearch 클라이언트 연결
def create_es_client():
    return Elasticsearch("http://localhost:9200")

# 2. 인덱스가 없다면 생성
def create_index(es, index_name):
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name)
        print(f"인덱스 '{index_name}'가 생성되었습니다.")
    else:
        print(f"인덱스 '{index_name}'는 이미 존재합니다.")

# 3. 문서 삽입
def insert_document(es, index_name, doc_id, doc):
    res = es.index(index=index_name, id=doc_id, body=doc)
    print(f"문서 삽입 결과(ID {doc_id}): {res['result']}") if res else print("문서 삽입 실패")

# 4. 문서 조회
def get_document(es, index_name, doc_id):
    try:
        res = es.get(index=index_name, id=doc_id)
        print(f"문서 조회 결과(ID {doc_id}): {res['_source']}")
        return res['_source']
    except NotFoundError:
        print(f"문서(ID {doc_id})가 존재하지 않습니다.")
        return None

# 5. 문서 수정 (부분 업데이트)
def update_document(es, index_name, doc_id, update_fields):
    try:
        res = es.update(index=index_name, id=doc_id, body={"doc": update_fields})
        print(f"문서 수정 결과(ID {doc_id}): {res['result']}") if res else print("문서 수정 실패")
    except NotFoundError:
        print(f"문서(ID {doc_id})가 존재하지 않아 수정할 수 없습니다.")

# 6. Upsert 기능
def upsert_document(es, index_name, doc_id, update_fields):
    res = es.update(
        index=index_name,
        id=doc_id,
        body={"doc": update_fields, "doc_as_upsert": True}
    )
    print(f"Upsert 결과(ID {doc_id}): {res['result']}") if res else print("Upsert 실패")

# 7. 문서 삭제
def delete_document(es, index_name, doc_id):
    try:
        res = es.delete(index=index_name, id=doc_id)
        print(f"문서 삭제 결과(ID {doc_id}): {res['result']}") if res else print("문서 삭제 실패")
    except NotFoundError:
        print(f"문서(ID {doc_id})가 존재하지 않아 삭제할 수 없습니다.")

# 메인 실행 흐름
if __name__ == "__main__":
    es = create_es_client()
    index_name = "products"
    doc_id = 1

    document = {
        "product_name": "Samsung Galaxy S25",
        "brand": "Samsung",
        "release_date": "2025-02-07",
        "price": 1199.99
    }

    create_index(es, index_name)
    insert_document(es, index_name, doc_id, document)
    get_document(es, index_name, doc_id)
    update_document(es, index_name, doc_id, {"price": 1099.99})
    get_document(es, index_name, doc_id)
    upsert_document(es, index_name, doc_id, {"price": 999.99})
    get_document(es, index_name, doc_id)
    delete_document(es, index_name, doc_id)
    get_document(es, index_name, doc_id)
    upsert_document(es, index_name, doc_id, {"price": 1399.99})
    get_document(es, index_name, doc_id)
```

<br>
<br>

📚 4\. 추가 설명 및 실무 팁
-------------------

### 🔐 실무에서 자주 마주치는 문제

| 상황                                 | 해결 방법                                                                      |
| ------------------------------------ | ------------------------------------------------------------------------------ |
| 인덱스 미리 존재하지 않아 에러 발생  | `es.indices.exists()` → 존재 여부 확인 후 `create()`                           |
| 문서 필드명이 잘못되거나 타입 불일치 | 사전에 Mapping 정의 또는 Index Template 활용 권장                              |
| `body` 파라미터의 구조 오류          | 반드시 `{"doc": {...}}` 또는 `{"doc": ..., "doc_as_upsert": True}` 형태로 전달 |
| 삭제 후 즉시 삽입 시 검색 누락       | ES는 비동기적 반영이므로 `refresh='wait_for'` 옵션 사용 가능                   |

### 🧠 심화 방향

*   `mapping` 명시 및 `analyzer`, `type` 지정 실습
    
*   `bulk API`를 활용한 대량 삽입 처리
    
*   `scripted update`로 수치형 필드에 대한 누적/증감 처리
    
*   Kibana DevTools 또는 Postman을 통한 API 테스트 병행
    
