# 이커머스 데이터 Bucket aggregation을 통한 데이터 검색

📘 1. 실습 주제 개요
--------------

### 🧩 주제: Nested Aggregation을 활용한 고객 그룹별 제품 분석

<br>

### 🔍 왜 배우는가?

Elasticsearch는 단순한 검색엔진이 아니라, **통계적 분석까지 가능한 데이터 플랫폼**입니다.  
특히 문서 내부에 배열 형태로 존재하는 **중첩 데이터(nested field)** 에 대해 **정확하게 그룹핑 및 집계**하려면 단순 Aggregation으로는 한계가 있습니다.

예를 들어, 고객 한 명이 여러 개의 제품을 구매한 경우, `"고객 성별이 남성이고"` `"모든 제품의 가격 평균을 알고 싶다"`는 질문에 정확하게 답하려면, **제품 배열 내부에서 집계가 가능해야 하며**, 이는 `nested aggregation`을 통해서만 가능합니다.

<br>

### 🎯 학습 목표

이번 실습을 통해 다음과 같은 내용을 학습합니다:

1.  **`nested` 필드 구조 복습** 및 집계 집합 모델링
    
2.  **Bulk API를 활용한 JSON 문서 삽입**
    
3.  **조건 기반 필터링(예: 성별 조건)** 후 **중첩 필드 집계 수행**
    
4.  **`value_count`와 `avg` Aggregation 사용법 숙지**
    
5.  **Elasticsearch에서 RDBMS처럼 분석 가능한 구조 설계 체득**
    

<br>

### 🧠 비유를 통한 이해

> 일반 Aggregation은 고객 전체의 쇼핑카트를 한데 섞어서 집계하는 것과 같습니다.  
> 하지만 Nested Aggregation은 각 고객의 쇼핑카트를 열어, **그 안의 물건만 정확하게 계산하는 방식**입니다.  
> 고객이 가진 정보는 바깥에, 고객의 장바구니는 안쪽에, **이 둘을 연결한 분석을 가능하게 해주는 도구가 nested aggregation**입니다.

<br>

### 🧪 실습을 통해 얻게 되는 효과

*   Elasticsearch를 **정제된 데이터 분석 도구로 활용하는 고급 기법**을 익힙니다.
    
*   **SQL의 GROUP BY와 유사한 기능을 Elasticsearch로 구현**하는 방법을 습득합니다.
    
*   실무에서 마주치는 **중첩된 반복 구조(리스트, 배열) 데이터를 정량화하는 기법**을 체득합니다.
    

<br>
<br>

🛠️ 2. 코드 구조 및 흐름 해설 + 실행 결과 예시
-------------------------------

### 🔄 전체 흐름 요약

이 코드는 다음과 같은 다섯 단계로 구성됩니다:

1.  기존 인덱스 삭제
    
2.  Nested 구조를 포함한 인덱스 생성
    
3.  Bulk API를 활용해 문서 삽입
    
4.  `customer_gender == "MALE"` 조건 필터링 후,
    
    *   products 배열 내부에서 제품 수(`value_count`)
        
    *   제품 가격 평균(`avg`)을 집계
        
5.  집계 결과 출력
    

<br>

### 💡 단계별 상세 해설

#### ✅ \[1\] 기존 인덱스 삭제

```python
if es.indices.exists(index=index_name):
    es.indices.delete(index=index_name)
```

*   이전에 생성된 인덱스를 제거하여 **재설정 충돌 방지**
    
*   실습 시 인덱스 매핑 변경이 자주 발생하므로 사전 삭제는 필수
    

📌 출력 예시:

```
[1] 기존 인덱스 [ecommerce] 삭제 완료
```

<br>

#### ✅ \[2\] 인덱스 생성 및 매핑

```python
"products": {
    "type": "nested",
    "properties": {
        "product_id": { "type": "keyword" },
        "category": { "type": "keyword" },
        "price": { "type": "double" }
    }
}
```

*   고객의 주문 데이터 중 **`products` 배열은 논리적으로 독립된 하위 문서**이므로 `nested` 타입으로 설정
    
*   이를 통해 **문서 내 반복 객체들을 정확하게 집계**할 수 있음
    

📌 출력 예시:

```
[2] 인덱스 [ecommerce] 생성 및 매핑 적용
```

<br>

#### ✅ \[3\] Bulk 데이터 삽입

```python
with open(json_path) ...
helpers.bulk(es, actions)
```

*   `ecommerce.json`은 Bulk API 형식에 맞춰 두 줄씩 구성됨 (메타 + 문서 본문)
    
*   `helpers.bulk()` 함수는 대량 데이터를 한 번에 색인
    

📌 출력 예시:

```
[3] Bulk 삽입 완료 및 인덱스 리프레시 완료
```

<br>

#### ✅ \[4\] Nested Bucket Aggregation 실행

```python
"query": {
    "term": {
        "customer_gender": "MALE"
    }
},
"aggs": {
    "products_nested": {
        "nested": { "path": "products" },
        "aggs": {
            "total_products": {
                "value_count": {
                    "field": "products.product_id"
                }
            },
            "avg_price": {
                "avg": {
                    "field": "products.price"
                }
            }
        }
    }
}
```

*   상위 문서 조건: **고객 성별이 "MALE"**
    
*   하위 nested 문서 조건 없이 전체 제품을 집계
    
*   `value_count`: 제품 수량
    
*   `avg`: 제품 가격 평균
    

📌 핵심 구조:

```mermaid
flowchart TD
    A[전체 고객 문서]
    A --> B[성별 = MALE 필터]
    B --> C[Nested 필드 접근: products]
    C --> D[제품 수 집계 (value_count)]
    C --> E[제품 평균 가격 (avg)]
```

<br>

#### ✅ \[5\] 결과 출력

```python
nested = response["aggregations"]["products_nested"]
print(f" - 전체 상품 수: {nested['total_products']['value']}")
print(f" - 평균 상품 가격: {nested['avg_price']['value']:.2f}")
```

📌 출력 예시:

```
[결과 요약]
 - 전체 상품 수: 21
 - 평균 상품 가격: 91.65
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
# [0] Elasticsearch 클라이언트 연결
# ----------------------------------------------
es = Elasticsearch("http://localhost:9200")  # 로컬 Elasticsearch 서버에 연결
index_name = "ecommerce"  # 사용할 인덱스 이름

# ----------------------------------------------
# [1] 기존 인덱스 삭제
# ----------------------------------------------
# 실습 또는 테스트 환경에서는 기존 인덱스를 삭제하고 새로 생성하는 것이 일반적
if es.indices.exists(index=index_name):
    es.indices.delete(index=index_name)
    print(f"[1] 기존 인덱스 [{index_name}] 삭제 완료")
else:
    print(f"[1] 기존 인덱스 [{index_name}] 없음, 새로 생성 진행")
time.sleep(2)

# ----------------------------------------------
# [2] 인덱스 생성 및 매핑
# ----------------------------------------------
print(f"[2] 인덱스 [{index_name}] 생성 및 매핑 적용")

# products 필드는 배열 형태이며, 각 항목이 논리적으로 독립된 문서 역할을 하므로 "nested" 타입을 사용
# 이를 통해 내부 요소 간 관계를 유지한 채 검색 및 집계가 가능
es.indices.create(
    index=index_name,
    body={
        "mappings": {
            "properties": {
                "order_id": { "type": "keyword" },  # 주문 ID (정렬 및 필터용)
                "customer_id": { "type": "integer" },
                "customer_gender": { "type": "keyword" },  # 성별 필터링을 위한 keyword 타입
                "total_price": { "type": "double" },
                "products": {
                    "type": "nested",  # 핵심: 중첩된 객체 배열
                    "properties": {
                        "product_id": { "type": "keyword" },
                        "category": { "type": "keyword" },
                        "price": { "type": "double" }
                    }
                }
            }
        }
    }
)
time.sleep(2)

# ----------------------------------------------
# [3] Bulk 데이터 삽입
# ----------------------------------------------
print("[3] Bulk 데이터 삽입 (ecommerce.json 사용)")

json_path = "../data/ecommerce.json"
if not os.path.exists(json_path):
    print(f"파일 없음: {json_path}")
    exit(1)

# Bulk 파일은 2줄 단위로 구성됨: 첫 줄은 메타정보, 두 번째 줄은 실제 문서
with open(json_path, "r", encoding="utf-8") as f:
    lines = f.read().splitlines()

actions = []
for i in range(0, len(lines), 2):
    action_line = json.loads(lines[i])     # {"index": {"_index": ..., "_id": ...}}
    doc_line = json.loads(lines[i + 1])    # 실제 문서 내용

    action_type, meta = list(action_line.items())[0]  # "index", metadata 추출
    index = meta.get("_index", index_name)
    doc_id = meta.get("_id")

    doc = {
        "_op_type": action_type,    # 색인 작업 유형 (index, create 등)
        "_index": index,
        "_source": doc_line
    }
    if doc_id:
        doc["_id"] = doc_id

    actions.append(doc)

# Bulk API를 통해 다수의 문서 삽입
helpers.bulk(es, actions)

# 삽입 직후 검색 가능하게 하기 위해 인덱스 리프레시 수행
es.indices.refresh(index=index_name)
print("[3] Bulk 삽입 완료 및 인덱스 리프레시 완료")
time.sleep(2)

# ----------------------------------------------
# [4] Nested Bucket Aggregation 실행
# ----------------------------------------------
print("[4] Nested Bucket Aggregation 실행 (MALE 고객의 상품 개수 및 평균 가격)")

query = {
    "size": 0,  # 검색 결과 자체는 출력하지 않음 (집계만 수행)
    "query": {
        "term": {
            "customer_gender": "MALE"  # 상위 문서(주문)의 성별 조건
        }
    },
    "aggs": {
        "products_nested": {
            "nested": { "path": "products" },  # nested 필드로 진입
            "aggs": {
                "total_products": {
                    "value_count": {
                        "field": "products.product_id"  # 총 제품 수
                    }
                },
                "avg_price": {
                    "avg": {
                        "field": "products.price"  # 평균 가격
                    }
                }
            }
        }
    }
}

# Aggregation 쿼리 실행
response = es.search(index=index_name, body=query)

# ----------------------------------------------
# [5] 결과 출력
# ----------------------------------------------
print("\n[결과 요약]")

# nested 필드 내 집계 결과 추출
nested = response["aggregations"]["products_nested"]
print(f" - 전체 상품 수: {nested['total_products']['value']}")
print(f" - 평균 상품 가격: {nested['avg_price']['value']:.2f}")
```

<br>
<br>

📚 4. 추가 설명 및 실무 팁
------------------

### ✅ Nested Aggregation이 필요한 이유

Elasticsearch는 문서 기반 검색 엔진이지만, 배열 구조에 대한 일반적인 집계는 **문서 내부 필드 간의 연관성을 고려하지 않습니다.**  
`nested` 타입은 이 문제를 해결하는 방식으로, 하위 객체들을 **별도의 독립 문서처럼 다루면서도 상위 문서와 논리적으로 연결**해줍니다.

#### 예시:

한 주문(`order`) 안에 여러 제품(`products`)이 있는 경우,

```json
"products": [
  { "product_id": "A1", "category": "Electronics", "price": 99.99 },
  { "product_id": "B2", "category": "Books", "price": 14.50 }
]
```

단순 Aggregation을 적용하면 **"Books 카테고리에 99.99"라는 잘못된 조합**이 만들어질 수 있습니다.  
Nested Aggregation은 이런 **잘못된 통계 왜곡을 방지**합니다.

<br>

### ⚠️ 자주 하는 실수 및 주의점

| 실수/이슈                        | 설명                                                                           |
| -------------------------------- | ------------------------------------------------------------------------------ |
| ❌ `nested` 선언 없이 Aggregation | 배열 구조를 `nested`로 명시하지 않으면 정확한 집계 불가                        |
| ❌ `path` 누락                    | `nested` Aggregation에서는 항상 `path`를 지정해야 함                           |
| ❌ 상위 쿼리 조건 누락            | 성별, 날짜, 지역 등 조건을 명시하지 않으면 집계 결과가 왜곡될 수 있음          |
| ❌ `size: 0` 누락                 | 집계만 하고 문서 자체는 필요 없을 경우 `size: 0`을 반드시 설정해야 성능 최적화 |

<br>

### 🧰 실무 활용 사례

#### 🛒 전자상거래 분석

*   고객 성별/연령별로 선호하는 카테고리 집계
    
*   특정 기간 내 평균 구매 금액 비교
    

#### 🏥 의료데이터 분석

*   환자별 투약 이력 중 약물명, 투약량, 처방 기간 평균 집계
    

#### 🧾 재무 분석

*   거래 내역 배열(nested)에서 거래 유형별 합계 및 평균 금액 계산
    
*   조건: 법인 사용자 + 특정 분기 기준
    

#### 💬 고객센터 로그

*   상담 세션 내 복수 메시지 중 “감정 점수 > 0.8” 조건에 해당하는 메시지 평균 수
    

<br>

### 📘 심화 학습 및 확장 아이디어

#### 1\. `terms` + `nested` Aggregation 조합

*   제품 카테고리별 평균 가격을 알고 싶을 경우:
    

```json
{
  "aggs": {
    "products_nested": {
      "nested": { "path": "products" },
      "aggs": {
        "by_category": {
          "terms": { "field": "products.category" },
          "aggs": {
            "avg_price": {
              "avg": { "field": "products.price" }
            }
          }
        }
      }
    }
  }
}
```

#### 2\. `reverse_nested` 활용

*   하위 집계 기준으로 상위 문서(고객 등) 다시 집계 가능 (예: 특정 제품 구매한 고객 수)
    

#### 3\. Kibana에서 시각화

*   Nested Aggregation도 Kibana Lens 또는 Visualization 기능을 통해 드릴다운 분석 가능
    

#### 4\. 성능 최적화

*   데이터 양이 많을 경우 Nested 필드는 디스크 사용량과 색인 시간이 급증할 수 있으므로, **적절한 필드 선택과 설계**가 중요합니다.
    

<br>

### 🧠 마무리 정리

이번 실습은 Elasticsearch의 검색 기능을 넘어서 **데이터 집계 및 통계 분석 도구로서의 역할을 체험**한 고급 예제입니다.  
Nested Aggregation은 SQL에서의 JOIN + GROUP BY와 유사한 구조를 비정형 문서에서 재현하는 기능으로,  
**복잡한 구조의 데이터도 정밀하게 분석할 수 있는 기반 역량**을 기를 수 있었습니다.

실무에서는 제품 분석, 사용자 행동 분석, IoT 로그 분석, 병원 EMR 데이터 분석 등 **다양한 분야에 적용 가능한 기술**입니다.
