# DataFrame vs SQL 성능 비교

📘 1. 실습 주제 개요 (이론, 목적, 왜 배우는지)
-------------------------------

**실습명: DataFrame API와 Spark SQL의 성능 비교 실습**

Spark는 대용량 데이터를 처리할 때 두 가지 대표적인 방식—**DataFrame API**와 **Spark SQL**—을 제공합니다. 이 두 방식은 기능적으로 유사한 결과를 도출할 수 있지만, **문법적 표현 방식**과 **실행 최적화 구조**에 있어 차이를 가집니다.

본 실습의 목적은 동일한 데이터를 기반으로 DataFrame API와 Spark SQL을 사용하여 **조건 필터링 및 집계 연산을 수행하고**, 이때의 **실행 시간 차이를 비교**함으로써 각각의 방식이 가지는 특성과 성능을 체감하는 데에 있습니다.

<br>

🛠️ 2. 코드 구조 및 흐름 해설 + 실행 결과 예시 및 해설
------------------------------------

### ✅ 전체 흐름 요약

1.  외부 CSV 파일을 불러와 Spark DataFrame으로 로드합니다.
    
2.  DataFrame API를 이용해 `Age >= 30` 조건에 맞는 행을 필터링하고 개수를 집계합니다.
    
3.  동일한 작업을 Spark SQL 쿼리 방식으로 수행합니다.
    
4.  각각의 방식에 소요된 처리 시간을 비교하여 어떤 방식이 더 빠른지 판단합니다.
    

<br>

### 📌 실행 흐름별 주요 코드와 출력 예시

#### ✅ 1단계: CSV 데이터 로드

```python
df = spark.read.option("header", True).option("inferSchema", True).csv("../data/people.csv")
```

-> `option("header", True)`: 첫 줄을 컬럼명으로 인식  
-> `option("inferSchema", True)`: 각 컬럼의 타입을 자동으로 추론  
-> `people.csv` 파일은 이름, 나이 등 인적 데이터가 포함되어 있는 구조입니다.


#### ✅ 2단계: DataFrame API 방식

```python
count_df = df.filter(col("Age") >= 30).count()
```

-> `col("Age") >= 30` 조건으로 필터링 후 개수 집계  
-> 시간 측정: `time.time()` 사용  

예시 출력:

```
DataFrame API 방식 - 30세 이상 인원 수: 19
DataFrame API 처리 시간: 0.124327초
```


#### ✅ 3단계: Spark SQL 방식

```python
df.createOrReplaceTempView("people")
count_sql = spark.sql("SELECT COUNT(*) FROM people WHERE AGE >= 30").collect()[0][0]
```

-> DataFrame을 SQL 쿼리에 사용할 수 있도록 임시 뷰로 등록한 뒤 SQL 문장 실행   

예시 출력:

```
Spark SQL 방식 - 30세 이상 인원 수: 19
Spark SQL 처리 시간: 0.143761초
```


#### ✅ 4단계: 성능 비교

```python
if elapsed_df < elapsed_sql:
    print("DataFrame API 방식이 더 빠릅니다.")
elif elapsed_sql < elapsed_df:
    print("Spark SQL 방식이 더 빠릅니다.")
else:
    print("두 방식의 성능이 거의 동일합니다.")
```

-> 실습 결과에 따라 방식의 우위를 비교하며, **데이터 크기나 실행 환경**에 따라 결과는 달라질 수 있습니다.

<br>

⚙️ 3. 전체 코드 + 상세 주석
-------------------

```python
# PySpark 사용을 위한 필수 라이브러리 불러오기
from pyspark.sql import SparkSession                 # SparkSession: Spark 기능의 진입점
from pyspark.sql.functions import col                # col(): 컬럼 지정 함수
import time                                          # 실행 시간 측정을 위한 모듈

# 1. SparkSession 생성 – 앱 이름 지정 후 세션 시작
spark = SparkSession.builder.appName("DataFrameVsSQL").getOrCreate()

# 2. CSV 파일 로드 – 사람들의 정보를 담은 외부 데이터 파일 로딩
# header=True: 첫 번째 행을 컬럼명으로 사용
# inferSchema=True: 자동으로 데이터 타입 추론
df = spark.read.option("header", True).option("inferSchema", True).csv("../data/people.csv")

# 3. DataFrame API 방식 실행
# 시간 측정 시작
start_df = time.time()

# 조건 필터링 (나이 30세 이상) 후 개수 집계
count_df = df.filter(col("Age") >= 30).count()

# 시간 측정 종료 및 경과 시간 계산
end_df = time.time()
elapsed_df = end_df - start_df

# DataFrame 방식 결과 출력
print(f"DataFrame API 방식 - 30세 이상 인원 수: {count_df}")
print(f"DataFrame API 처리 시간: {elapsed_df:.6f}초")

# 4. Spark SQL 방식 실행
# 먼저 DataFrame을 SQL에서 사용 가능하도록 임시 뷰로 등록
df.createOrReplaceTempView("people")

# 시간 측정 시작
start_sql = time.time()

# SQL 쿼리 실행 – 나이 조건을 만족하는 행 개수 조회
count_sql = spark.sql("SELECT COUNT(*) FROM people WHERE AGE >= 30").collect()[0][0]

# 시간 측정 종료 및 경과 시간 계산
end_sql = time.time()
elapsed_sql = end_sql - start_sql

# Spark SQL 방식 결과 출력
print(f"Spark SQL 방식 - 30세 이상 인원 수: {count_sql}")
print(f"Spark SQL 처리 시간: {elapsed_sql:.6f}초")

# 5. 두 방식의 실행 시간 비교 및 결론 출력
if elapsed_df < elapsed_sql:
    print("DataFrame API 방식이 더 빠릅니다.")
elif elapsed_sql < elapsed_df:
    print("Spark SQL 방식이 더 빠릅니다.")
else:
    print("두 방식의 성능이 거의 동일합니다.")
```

위 코드는 **조건 필터링 및 집계 연산을 서로 다른 방식으로 수행하고, 처리 속도까지 비교**해보는 대표적인 실습 예제입니다.

<br>

📚 4. 추가 설명 및 실무 팁 (자주 하는 실수, 심화 방향 등)
--------------------------------------

### ✅ DataFrame API vs Spark SQL 비교 요약

| 항목        | DataFrame API                                | Spark SQL                               |
| ----------- | -------------------------------------------- | --------------------------------------- |
| 문법 스타일 | 함수형 (Functional)                          | SQL 문장 기반 (Declarative)             |
| 코드 구조   | 명확한 연산 체인 구조                        | SQL 문법에 익숙한 사용자에게 유리       |
| 사용 용도   | 프로그램 내에서 동적 조건 처리               | 리포트, 대시보드, 쿼리 기반 분석에 적합 |
| 성능 차이   | 거의 동일 (Catalyst 엔진이 내부 최적화 처리) | 동일한 Catalyst 엔진 사용               |

> 💡 **중요한 사실**: 성능 차이는 대부분 **코드 작성 방식보다는 데이터 크기, 클러스터 설정, 캐싱 여부 등에 의해 결정**됨.

<br>

### 🔍 자주 하는 실수 및 주의할 점

#### 1️⃣ `.collect()` 사용 시 주의

*   `spark.sql(...).collect()`은 전체 데이터를 드라이버 메모리로 가져옴 → 대용량일 경우 메모리 부족 발생
    
*   ✅ 실무에서는 `limit()`과 함께 사용하거나 `.show()`로 미리보기 수행
    

#### 2️⃣ SQL 구문 내 컬럼명 대소문자 주의

*   Spark는 대소문자를 구분하지 않지만, 실제 운영 환경에서는 구분되는 시스템도 있음
    
*   `"SELECT COUNT(*) FROM people WHERE AGE >= 30"`처럼 항상 명확한 컬럼명을 사용하는 습관 필요
    

#### 3️⃣ 성능 테스트는 반복 실험 필요

*   한 번의 시간 측정으로 성능을 일반화하지 말 것
    
*   **여러 번 실행 후 평균값 비교**가 바람직
    
<br>

### 🚀 실무 확장 방향

#### 💼 활용 예시

*   실시간 스트리밍 데이터의 조건 필터링 및 통계 집계
    
*   사용자 행동 로그에서 연령대 필터 후 분석
    
*   대용량 CSV/Parquet/ORC 등 다양한 포맷 파일에 대한 조회
    

#### 📈 확장 학습 주제

| 주제                       | 설명                                                    |
| -------------------------- | ------------------------------------------------------- |
| `explain()` 함수           | 실행 계획 확인으로 성능 최적화 힌트 제공                |
| DataFrame 캐싱             | `.cache()`로 자주 조회하는 테이블을 메모리에 저장       |
| Broadcast Join             | 소규모 테이블을 전체 클러스터에 복사하여 join 속도 향상 |
| UDF(User Defined Function) | 사용자 정의 함수로 비표준 연산 적용 가능                |

<br>

### ✅ 마무리 요약

이번 실습은 Spark의 두 가지 주요 API 사용법을 직접 비교하며, **단순한 집계 연산도 방식에 따라 다양한 코드 스타일로 구현 가능**하다는 점을 경험하는 것이 핵심이었습니다. 두 방식은 내부적으로 동일한 최적화 엔진(Catalyst)을 사용하므로, 성능보다는 **개발자의 익숙함과 상황에 맞는 선택**이 중요합니다.

데이터 분석이나 서비스 로그 분석 업무를 준비하는 입장에서, 이번 실습은 Spark의 기본 구조와 최적화 관점을 함께 체득할 수 있는 좋은 출발점이 됩니다.
