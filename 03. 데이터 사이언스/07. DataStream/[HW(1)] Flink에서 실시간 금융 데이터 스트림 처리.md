# 실습 정리본 작성 요청

**User:** 장철환(하냥) (wkdcjfghks1@gmail.com)  
**Created:** 5/11/2025 11:48  
**Updated:** 5/11/2025 12:27  
**Exported:** 5/11/2025 12:32  

## Response:
좋아, 이번 실습은 이전의 `reduce()` 기반 집계보다 간결하고 직관적인 방식으로, PyFlink의 `.sum()` 연산자를 활용한 **Keyed Stream 기반 실시간 누적 집계** 구조야.  
지금까지와 동일하게 아래 네 가지 항목으로 구성된 정리본을 순차적으로 제공할게:

* * *

### ✅ 구성 방식

1.  📘 실습 주제 개요
    
2.  🛠️ 코드 구조 및 흐름 해설 + 실행 결과 예시 및 해설
    
3.  ⚙️ 전체 코드 + 상세 주석
    
4.  📚 추가 설명 및 실무 팁
    

* * *

지금부터 **1\. 실습 주제 개요**를 먼저 설명해줄게.

* * *

📘 1\. 실습 주제 개요
---------------

이번 실습은 PyFlink의 `DataStream API`를 사용하여 거래 데이터의 `"transaction_type"`별 `"amount"`를 **누적 합산하는 파이프라인**을 구현하는 것이다.  
이전 실습에서는 `reduce()` 연산자를 사용했지만, 이번에는 보다 간결하고 직관적인 `.sum()` 연산자를 활용하여 같은 목적을 달성한다.

`.sum()`은 Flink에서 제공하는 기본적인 집계 연산 중 하나로, key별 그룹핑이 완료된 데이터에 대해 특정 필드를 기준으로 누적 합을 자동으로 계산한다.  
따라서, 실시간 통계나 재무 데이터, 센서 데이터 등에서 카테고리별 누적 합을 빠르고 안정적으로 계산할 수 있다.

* * *

### 실습 흐름

> Pandas CSV 로드 → (transaction\_type, amount) 튜플 스트림 생성  
> → `key_by(transaction_type)`  
> → `sum(amount)`  
> → 실시간 출력

* * *

### 학습 목표

*   `.key_by(...).sum(...)`의 실시간 집계 흐름 이해
    
*   Flink의 내장 집계 연산자의 장단점 학습
    
*   데이터 타입 명시 및 스트림 생성 방식 익히기
    
*   Pandas 정적 데이터를 Flink 스트림 입력으로 활용하는 방법 익히기
    

* * *

이제 다음 메시지에서는 **2\. 코드 구조 및 흐름 해설 + 실행 결과 예시 및 해설**을 아주 상세히 설명해줄게.  
바로 이어서 진행할게.

## Response:
좋아, 이제 **2\. 코드 구조 및 흐름 해설 + 실행 결과 예시 및 해설**을 상세하게 설명해줄게.  
이번 실습은 `.key_by().sum()`을 통해 **간결하게 누적 집계를 처리하는 PyFlink 구조**를 학습하는 데 초점이 있어.

* * *

🛠️ 2\. 코드 구조 및 흐름 해설 + 실행 결과 예시 및 해설
-------------------------------------

* * *

### 🔧 1단계: 실행 환경 설정

```python
env = StreamExecutionEnvironment.get_execution_environment()
```

*   Flink 스트리밍 실행 환경을 생성하는 기본 호출
    
*   내부적으로 연산자를 DAG 형태로 정의하고, 실행 시 TaskManager가 병렬 처리하게 됨
    

* * *

### 📄 2단계: 데이터 불러오기 및 전처리

```python
df = pd.read_csv("../data/data.csv")
transactions = df[["transaction_type", "amount"]].dropna().values.tolist()
```

*   Pandas를 사용해 CSV 파일에서 필요한 두 컬럼만 선택 (`transaction_type`, `amount`)
    
*   결측값 제거 후, `.values.tolist()`로 Flink가 다룰 수 있는 리스트\[튜플\] 형태로 변환  
    예: `[["purchase", 100.0], ["refund", 30.5], ["purchase", 70.0]]`
    

* * *

### 🌊 3단계: PyFlink 스트림 생성

```python
transaction_stream = env.from_collection(
    transactions,
    type_info=Types.TUPLE([Types.STRING(), Types.FLOAT()])
)
```

*   Flink에서 사용 가능한 스트림으로 변환
    
*   `Types.TUPLE(...)` 명시적 타입 선언 필요 (PyFlink는 TypeInfo 기반 정적 타입 시스템을 사용)
    

* * *

### ➕ 4단계: 거래 유형별 누적 금액 계산

```python
total_amount_per_type = (
    transaction_stream
    .key_by(lambda x: x[0])  # 거래 유형 기준 그룹화
    .sum(1)  # 두 번째 필드(금액)를 기준으로 합산
)
```

*   `key_by(...)`: 거래 유형별로 데이터를 파티셔닝
    
*   `sum(1)`: 각 그룹 내에서 두 번째 필드(index=1, 즉 amount)의 값을 누적 합산
    
*   `sum()`은 Flink 내부적으로 상태(state)를 유지하며 자동으로 합산을 관리
    

예시 흐름:

```
("purchase", 100.0)
("purchase", 70.0) → sum → ("purchase", 170.0)
("refund", 30.0)
```

* * *

### 📤 5단계: 결과 출력 및 실행

```python
total_amount_per_type.print()
env.execute("Streaming Transaction Processing")
```

*   `print()`: 콘솔 출력용 내장 Sink 함수
    
*   `env.execute(...)`: DAG 실행 트리거 (없으면 작업이 실행되지 않음)
    

* * *

### 🖥️ 실행 결과 예시

입력:

```csv
transaction_type,amount
purchase,100
refund,30
purchase,70
```

출력:

```
(purchase, 100.0)
(refund, 30.0)
(purchase, 170.0)
```

*   실시간 스트리밍이므로 결과 순서는 병렬성 설정 및 키 도착 순서에 따라 유동적일 수 있음
    

* * *

이제 다음 메시지에서는 위의 코드를 **하나도 생략하지 않고**, **각 라인에 상세한 설명 주석을 포함한 형태로**  
**3\. 전체 코드 + 상세 주석**으로 제공할게.  
바로 이어서 진행할게.

## Response:
좋아, 이제 **3\. 전체 코드 + 상세 주석**을 제공할게.  
이 코드는 `reduce()`보다 간단하지만, 내부적으로는 Flink의 상태 관리와 key 기반 집계의 본질을 그대로 담고 있어.  
모든 코드 줄마다 자세한 주석을 달아, PyFlink 흐름을 확실히 이해할 수 있도록 정리했어.

* * *

⚙️ 3\. 전체 코드 + 상세 주석
--------------------

```python
import pandas as pd
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common.typeinfo import Types

def main():
    # Flink 스트리밍 실행 환경을 생성 (Flink 프로그램의 진입점)
    env = StreamExecutionEnvironment.get_execution_environment()

    # CSV 파일을 Pandas로 로드
    df = pd.read_csv("../data/data.csv")

    # 'transaction_type'과 'amount' 컬럼만 추출하고 결측값 제거
    transactions = df[["transaction_type", "amount"]].dropna().values.tolist()
    # 예: [["purchase", 100.0], ["refund", 50.0], ["purchase", 30.0]]

    # PyFlink 스트림 생성: 각 요소는 (문자열, 실수형) 튜플로 지정
    transaction_stream = env.from_collection(
        transactions,
        type_info=Types.TUPLE([Types.STRING(), Types.FLOAT()])
    )

    # 거래 유형별로 그룹핑 후 금액 누적합을 계산하는 파이프라인 구성
    total_amount_per_type = (
        transaction_stream
        .key_by(lambda x: x[0])   # 첫 번째 필드(transaction_type)를 기준으로 그룹핑
        .sum(1)                   # 두 번째 필드(amount)를 누적 합산
    )

    # 집계 결과를 실시간으로 출력 (console sink)
    total_amount_per_type.print()

    # Flink 스트림 처리 시작 (실행 명령 없으면 파이프라인 작동하지 않음)
    env.execute("Streaming Transaction Processing")

# Python 프로그램의 진입점: 직접 실행될 경우 main() 호출
if __name__ == "__main__":
    main()
```

* * *

이 코드 구조는 **카테고리별 실시간 수치 집계의 가장 단순하면서도 강력한 형태**를 보여주며,  
Flink의 \*\*상태 저장 처리(Stateful Processing)\*\*를 직관적으로 학습할 수 있는 매우 좋은 실습 예제야.

다음 메시지에서는 마지막으로 **📚 4\. 추가 설명 및 실무 팁**을 정리해서 실무 적용, 확장 전략, 주의사항 등을 체계적으로 안내할게.  
바로 이어서 진행할게.

## Response:
좋아, 이제 마지막 항목인 **📚 4\. 추가 설명 및 실무 팁**을 정리해줄게.  
이번 실습은 PyFlink의 `key_by().sum()`을 사용하여 **스트리밍 집계를 가장 간단하고 안정적으로 구현**하는 방법을 보여줬어. 여기서 배운 개념은 실무에 그대로 적용될 수 있어.

* * *

📚 4\. 추가 설명 및 실무 팁
-------------------

* * *

### ✅ `.key_by().sum()`의 실무적 의미

`.sum()`은 Flink 내부에서 다음과 같이 동작해:

1.  `key_by()`를 통해 동일 키(`transaction_type`)를 가진 레코드가 동일 파티션으로 라우팅됨
    
2.  각 키에 대해 **Flink가 자동으로 상태(state)를 유지**함
    
3.  새로운 값이 들어올 때마다 누적 합산 수행 (reduce보다 간결, 안정적)
    

이는 \*\*상태 기반 집계(stateful aggregation)\*\*의 가장 직관적인 구현 방식이자, 실시간 수치 분석에서 자주 사용되는 패턴이야.

* * *

### 💡 실무에서 사용하는 대표 사례

| 사례 | 설명 |
| --- | --- |
| 실시간 결제 수집 | 거래 유형별 실시간 누적 금액 |
| 이벤트 로그 수집 | 이벤트 타입별 발생 횟수/합계 |
| 실시간 광고 분석 | 캠페인 ID별 클릭/노출 합산 |
| IoT 센서 분석 | 장비 ID별 누적 에너지, 온도 수치 |

* * *

### ⚠️ 자주 하는 실수와 주의점

| 실수 | 해결 방법 |
| --- | --- |
| `sum(1)` 필드 위치 실수 | DataStream 튜플의 인덱스를 정확히 확인해야 함 (`sum("amount")`은 Table API에서만 가능) |
| 소수점 손실 | `int`가 아닌 `float`로 명시해야 함 (`Types.FLOAT()` 또는 `Types.DOUBLE()`) |
| 키가 `None` 또는 공백 | keyBy 대상 필드의 정합성 검사 필수 (Flink는 None 키를 허용하지 않음) |
| `env.execute()` 누락 | Flink는 명령 정의 후 `execute()` 호출해야 실제 실행됨 |

* * *

### 🔁 실무 확장 방향

#### ✅ 1\. Kafka 실시간 연동

*   `from_collection()` 대신 KafkaConsumer로 실시간 거래 데이터를 받아 처리
    
*   결과는 KafkaProducer 또는 PostgreSQL 등에 저장
    

#### ✅ 2\. Window 연산 도입

*   단순 누적이 아닌 "최근 5분", "매 1시간", "하루" 단위 집계를 원할 경우:
    

```python
from pyflink.datastream.window import TumblingProcessingTimeWindows
from pyflink.common.time import Time

transaction_stream \
    .key_by(lambda x: x[0]) \
    .window(TumblingProcessingTimeWindows.of(Time.minutes(5))) \
    .sum(1)
```

#### ✅ 3\. Table API 전환

*   SQL 스타일 집계로 전환 가능:
    

```sql
SELECT transaction_type, SUM(amount)
FROM transactions
GROUP BY transaction_type
```

#### ✅ 4\. 결과 저장 또는 시각화

*   `.add_sink()`를 통해 다음으로 저장 가능:
    
    *   파일(CSV, Parquet)
        
    *   PostgreSQL
        
    *   Elasticsearch → Kibana
        
    *   Prometheus + Grafana
        

* * *

### ✅ 마무리 요약

*   이 실습은 Flink 스트리밍 데이터 처리의 기본이 되는 **keyed state + 누적 집계**를 가장 간단한 방식으로 구현한 예제다.
    
*   `key_by().sum()`은 처리 로직이 단순한 만큼 **초기 실시간 분석 시스템 구성에서 필수적으로 사용**되는 연산이다.
    
*   이후 `reduce()`, `window()`, `process()` 등으로 점진적으로 확장하면서 실시간 분석 시스템을 보다 정교하게 발전시킬 수 있다.
    

* * *

이제 이 실습도 완벽하게 정리되었어.  
다음으로 Table API 버전으로 같은 집계를 해보거나, Kafka에서 실시간으로 데이터를 받아서 처리하는 파이프라인으로 확장해보고 싶다면 언제든 도와줄게!  
어떻게 이어서 진행할까?



---
Powered by [ChatGPT Exporter](https://www.chatgptexporter.com)