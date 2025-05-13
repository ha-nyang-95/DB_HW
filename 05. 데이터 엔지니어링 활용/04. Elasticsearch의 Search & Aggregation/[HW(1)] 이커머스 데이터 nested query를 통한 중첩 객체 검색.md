# 이커머스 데이터 nested query를 통한 중첩 객체 검색

📘 1. 실습 주제 개요
--------------

### 🧩 주제: Elasticsearch Nested 데이터 구조 이해 및 쿼리 실습

<br>

### 🔍 왜 배우는가?

Elasticsearch는 **JSON 기반의 비정형 데이터**를 저장하고 검색할 수 있는 강력한 검색 엔진입니다. 그러나 복잡한 구조의 문서, 예를 들어 **“하나의 주문이 여러 제품을 포함하는 구조”** 에서는 일반적인 필드 매핑으로는 정확한 검색이 어렵습니다.

예를 들어, 한 주문에 여러 제품이 포함되어 있는데, `"제품 제조사 = Elitelligence"`라는 조건으로 검색할 경우, 일반적인 구조에서는 다른 제품 정보가 혼합되어 검색 정확도가 떨어질 수 있습니다.

이를 해결하기 위해 Elasticsearch는 **`nested` 타입**을 제공합니다. 이 구조는 **하위 문서(자식 요소)를 독립된 객체로 색인**함으로써, **부정확한 매칭을 방지하고, 조인 없는 정교한 검색이 가능**하게 합니다.

<br>

### 🎯 학습 목표

이번 실습에서는 다음과 같은 내용을 학습합니다:

1.  **Nested 구조로 인덱스 매핑 설계**
    
2.  **Bulk API를 사용한 대용량 JSON 문서 삽입**
    
3.  **Nested Query 문법과 `inner_hits` 사용법 이해**
    
4.  **복잡한 문서 구조에서 정확한 조건 검색 수행**
    

<br>

### 🧠 비유를 통한 이해

> 일반 텍스트 필드 검색은 “책 안의 단어가 있는지만 확인”하는 방식입니다.  
> 반면 `nested`는 “책 안에 있는 **특정 챕터에서만** 단어가 나오는지 확인”하는 방식입니다.  
> 즉, **연관된 정보가 실제 같은 하위 객체 내에 있는지**까지 확인하는 정교한 구조입니다.

<br>

### 🧪 실습을 통해 얻게 되는 효과

*   관계형 DB에서의 **1:N 관계 모델링을 NoSQL 환경에서 구현**하는 방법을 익힙니다.
    
*   **상품, 사용자, 댓글, 리뷰 등 계층적 데이터 구조**를 색인하고 검색하는 능력을 기릅니다.
    
*   실무에서 자주 사용하는 **복합 객체 필드 모델링과 검색 쿼리 설계 역량**을 확보하게 됩니다.
    

<br>
<br>

🛠️ 2. 코드 구조 및 흐름 해설 + 실행 결과 예시
-------------------------------

### 🔄 전체 흐름 요약

이번 실습은 다음과 같은 단계로 구성되어 있습니다:

1.  기존 인덱스 삭제
    
2.  `nested` 타입을 포함한 인덱스 매핑 설정 및 생성
    
3.  Bulk API를 통한 JSON 파일 데이터 일괄 삽입
    
4.  `nested` 쿼리 실행 및 `inner_hits`로 정확한 일치 결과 확인
    
5.  고객별 검색 결과 출력
    

<br>

### 💡 단계별 상세 해설

#### ✅ 1단계: 기존 인덱스 삭제

```python
if es.indices.exists(index=index_name):
    es.indices.delete(index=index_name)
```

*   동일 이름의 인덱스가 존재할 경우 삭제하고 새로 생성합니다.
    
*   인덱스 설정 변경 시 일반적으로 삭제 후 재생성이 필요합니다.
    

📌 출력 예시:

```
1. 기존 인덱스 [ecommerce] 삭제 완료
```

<br>

#### ✅ 2단계: `nested` 필드가 포함된 인덱스 생성

```python
"products": {
    "type": "nested",
    "properties": {
        "product_name": { "type": "text" },
        "price": { "type": "double" },
        "category": { "type": "keyword" },
        "manufacturer": { "type": "keyword" }
    }
}
```

*   각 주문은 여러 제품을 포함할 수 있으며, 이를 위해 `products` 필드를 `nested` 타입으로 선언합니다.
    
*   `nested` 타입은 Elasticsearch 내부적으로 하위 문서를 별도로 저장하여 **상위 문서의 다른 필드와 혼동 없이 쿼리 가능**하게 만듭니다.
    

📌 출력 예시:

```
2. 인덱스 [ecommerce] 생성 및 매핑 적용
```

<br>

#### ✅ 3단계: Bulk API로 JSON 문서 삽입

```python
with open(json_path, "r", encoding="utf-8") as f:
    bulk_data_lines = f.readlines()
```

*   `ecommerce.json` 파일은 **두 줄씩 쌍으로** 구성되어 있음 (1줄은 메타정보, 1줄은 문서 본문)
    
*   `helpers.bulk` 함수는 수천 건 이상의 문서를 **한 번의 요청으로 색인** 가능하여 대용량 데이터 삽입에 매우 유리합니다.
    

📌 출력 예시:

```
3. Bulk 삽입 완료 및 refresh
```

<br>

#### ✅ 4단계: `nested` 쿼리 실행

```python
"nested": {
    "path": "products",
    "query": {
        "bool": {
            "must": [
                { "match": { "products.manufacturer": "Elitelligence" } }
            ]
        }
    },
    "inner_hits": {}
}
```

*   `nested` 필드에서 조건을 만족하는 하위 문서만을 대상으로 검색 수행
    
*   `path`는 어떤 필드를 대상으로 할 것인지 지정
    
*   `inner_hits`는 일치한 **하위 문서(products 배열의 요소)** 만 별도로 추출하는 기능
    

📌 출력 예시 (일부):

```
4. Nested Query 실행 (제조사가 'Elitelligence'인 제품 검색)
```

<br>

#### ✅ 5단계: 결과 출력 (내부 문서 조회)

```python
for hit in response["hits"]["hits"]:
    customer = hit["_source"].get("customer_full_name", "(이름 없음)")
    inner_hits = hit.get("inner_hits", {}).get("products", {}).get("hits", {}).get("hits", [])
    for inner in inner_hits:
        p = inner["_source"]
        print(f"  → 제품명: {p['product_name']}, 제조사: {p['manufacturer']}")
```

*   상위 문서(주문) 중 조건을 만족하는 하위 문서(제품)의 세부 정보를 출력합니다.
    
*   `inner_hits`를 활용하면 조건에 맞는 제품만 정확히 추출 가능
    

📌 결과 예시:

```
고객: 김민수
  → 제품명: 스마트워치 Z5, 제조사: Elitelligence
  → 제품명: AI스피커 Vibe, 제조사: Elitelligence
```

<br>
<br>

⚙️ 3. 전체 코드 + 상세 주석
-------------------

```python
from elasticsearch import Elasticsearch, helpers
import json
import time
import os

# ----------------------------------------------
# 1. Elasticsearch 클라이언트 생성
# ----------------------------------------------
# 로컬에서 실행 중인 Elasticsearch 인스턴스에 연결
es = Elasticsearch("http://localhost:9200")
index_name = "ecommerce"  # 생성할 인덱스 이름

# ----------------------------------------------
# 2. 기존 인덱스 삭제
# ----------------------------------------------
# 동일한 인덱스가 존재하면 삭제 (중복 에러 방지 및 설정 재적용 목적)
if es.indices.exists(index=index_name):
    es.indices.delete(index=index_name)
    print(f"1. 기존 인덱스 [{index_name}] 삭제 완료")
else:
    print(f"1. 기존 인덱스 [{index_name}] 없음, 새로 생성 진행")
time.sleep(2)

# ----------------------------------------------
# 3. Nested 매핑 포함한 인덱스 생성
# ----------------------------------------------
print(f"2. 인덱스 [{index_name}] 생성 및 매핑 적용")

# 주문(customer) 문서 내에 포함된 여러 제품(products)을 nested 타입으로 명시
es.indices.create(
    index=index_name,
    body={
        "settings": {
            "number_of_shards": 1,     # 단일 샤드 사용 (소규모 실습 기준)
            "number_of_replicas": 0    # 복제본 없음 (단일 노드 환경 가정)
        },
        "mappings": {
            "properties": {
                "customer_full_name": { "type": "text" },
                "order_id": { "type": "keyword" },
                "order_date": { "type": "date" },
                "total_quantity": { "type": "integer" },
                "total_unique_products": { "type": "integer" },
                "products": {
                    "type": "nested",  # 핵심: 배열 내 문서가 논리적으로 독립적임을 명시
                    "properties": {
                        "product_name": { "type": "text" },
                        "price": { "type": "double" },
                        "category": { "type": "keyword" },
                        "manufacturer": { "type": "keyword" }
                    }
                }
            }
        }
    }
)
time.sleep(2)

# ----------------------------------------------
# 4. Bulk API를 통한 데이터 삽입
# ----------------------------------------------
print("3. 'ecommerce.json' 파일을 이용한 Bulk 삽입")

json_path = "../data/ecommerce.json"  # JSON 경로 설정
if not os.path.exists(json_path):
    print(f"파일 없음: {json_path}")
    exit(1)

# Bulk 파일은 2줄씩 구성됨: 1줄은 액션 메타, 1줄은 문서 본문
with open(json_path, "r", encoding="utf-8") as f:
    bulk_data_lines = f.readlines()

actions = []
for i in range(0, len(bulk_data_lines), 2):
    action = json.loads(bulk_data_lines[i])      # {"index": {"_index": "ecommerce"}}
    doc = json.loads(bulk_data_lines[i + 1])      # 문서 본문
    index = action["index"]["_index"]
    doc_id = action["index"].get("_id")
    action_doc = {"_index": index, "_source": doc}
    if doc_id:
        action_doc["_id"] = doc_id
    actions.append(action_doc)

# helpers.bulk: 다량의 문서를 한 번에 색인 (고속)
helpers.bulk(es, actions)

# 색인 후 검색을 위해 인덱스 리프레시 필요
es.indices.refresh(index=index_name)

print("3. Bulk 삽입 완료 및 refresh")
time.sleep(2)

# ----------------------------------------------
# 5. Nested Query 실행
# ----------------------------------------------
print("4. Nested Query 실행 (제조사가 'Elitelligence'인 제품 검색)")

query = {
    "size": 3,  # 상위 문서 최대 3개 반환
    "query": {
        "nested": {
            "path": "products",  # nested 필드 지정
            "query": {
                "bool": {
                    "must": [
                        { "match": { "products.manufacturer": "Elitelligence" } }
                    ]
                }
            },
            "inner_hits": {}  # 하위 문서(products 배열 중 일치 항목만 반환)
        }
    }
}

# 검색 실행
response = es.search(index=index_name, body=query)

# ----------------------------------------------
# 6. 검색 결과 출력
# ----------------------------------------------
print("5. 검색 결과 출력")

# 상위 문서(customer) 기준으로 출력, 각 문서의 inner_hits(products)에서 조건 일치 항목만 추출
for hit in response["hits"]["hits"]:
    customer = hit["_source"].get("customer_full_name", "(이름 없음)")
    print(f"\n고객: {customer}")
    inner_hits = hit.get("inner_hits", {}).get("products", {}).get("hits", {}).get("hits", [])
    for inner in inner_hits:
        p = inner["_source"]
        print(f"  → 제품명: {p['product_name']}, 제조사: {p['manufacturer']}")

print("\nElasticsearch Nested Query 테스트 완료!")
```

<br>
<br>

📚 4. 추가 설명 및 실무 팁
------------------

### ✅ 실무에서 Nested 타입이 필요한 이유

Elasticsearch는 JSON 문서를 기반으로 데이터를 색인하고 검색합니다. 하지만 단순한 배열(`array`) 타입은 내부 필드 간 관계를 보장하지 않기 때문에, **의도하지 않은 필드 조합**으로 매칭되는 오류가 발생할 수 있습니다.

#### 예시:

```json
{
  "customer": "김민수",
  "products": [
    { "product_name": "스마트워치 Z5", "manufacturer": "Elitelligence" },
    { "product_name": "무선 이어폰 S2", "manufacturer": "OtherBrand" }
  ]
}
```

> 일반 쿼리에서는 `"product_name": "무선 이어폰 S2"`와 `"manufacturer": "Elitelligence"`가 **같은 제품으로 잘못 연결**되어 매칭될 수 있습니다.

이를 해결하기 위해 사용하는 것이 바로 **`nested` 타입**입니다. `nested`는 각 배열 요소를 **독립적인 하위 문서로 처리**하여 필드 간의 정확한 관계를 유지할 수 있게 해줍니다.

<br>

### ⚠️ 자주 하는 실수 및 주의점

| 실수/오해                        | 설명                                                                                              |
| -------------------------------- | ------------------------------------------------------------------------------------------------- |
| ❌ `nested`가 아닌 배열 구조 사용 | 배열만 사용하면 필드 간 관계가 깨지고 쿼리 결과가 왜곡됩니다.                                     |
| ❌ `path` 누락 또는 오타          | `nested` 쿼리를 작성할 때 `path`는 반드시 지정되어야 하며, 필드 이름과 정확히 일치해야 합니다.    |
| ❌ `inner_hits` 누락              | 조건에 일치한 하위 문서를 보고자 할 때 `inner_hits`를 명시하지 않으면 결과에 포함되지 않습니다.   |
| ❌ 너무 복잡한 `nested` 중첩      | 중첩이 깊어지면 색인 및 쿼리 성능이 급격히 저하될 수 있습니다. 2단계 중첩을 넘기면 구조 재고 필요 |

<br>

### 🔍 실무 활용 사례

#### 1\. 전자상거래

*   고객 주문 문서 안에 여러 제품
    
*   제품별 제조사, 가격, 리뷰 등 상세 필드
    
*   조건: “리뷰 점수가 4점 이상인 삼성 제품 포함된 주문만 검색”
    

#### 2\. 소셜미디어

*   게시글 내부에 여러 댓글
    
*   댓글 작성자, 내용, 작성일 등 중첩
    
*   조건: “욕설이 포함된 댓글이 있는 게시글 찾기”
    

#### 3\. 금융 거래 로그

*   하나의 트랜잭션 안에 여러 거래 항목
    
*   조건: “상품 코드 A001이 포함된 모든 거래 내역”
    

<br>

### 📘 심화 학습 방향

#### 1\. `nested` + `range` 조건 복합 쿼리

*   특정 가격 이상 또는 이하인 제품만 필터링
    

#### 2\. `nested` + `script` 스코어링

*   조건을 만족하는 제품 개수에 따라 상위 문서(주문)의 랭킹을 조정
    

#### 3\. `nested` Aggregation

*   제품 제조사별 판매량, 카테고리별 통계 등을 구할 수 있음 (단, `nested` aggregation 필요)
    

#### 4\. `flattened` 타입 비교 학습

*   `nested`보다 검색은 빠르지만 정밀한 관계를 포기하는 타입
    
*   대규모 분석용 문서에 적합
    

<br>

### 🧠 마무리 정리

이번 실습은 단일 문서 내부에 **논리적으로 독립된 구조를 안전하게 저장하고 검색하는 방법**을 다룬 고급 실습입니다.  
이를 통해 JSON 기반 문서를 다룰 때 **정확한 매칭을 보장하는 설계 능력**을 키울 수 있었으며, `nested` 쿼리를 통해 실질적인 조건 매칭, 하위 문서 추출, 결과 해석 능력을 함께 체득할 수 있었습니다.

단순한 텍스트 기반 검색을 넘어서 **구조화된 문서 내 의미 있는 조합을 정밀하게 탐색**할 수 있는 실무 능력을 기르게 되는 것이 이 실습의 핵심입니다.
