📘 Spark Shell에서 기본 연산 수행
=====================

> 이 문서는 PySpark를 활용한 기본 데이터 생성 및 변환 실습 예제를 바탕으로 작성되었습니다. 비전공자도 이해할 수 있도록 각 단계에서 어떤 개념이 사용되었는지 함께 설명합니다.


✅ 1. Spark 환경 설정
----------------

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("Transformations").getOrCreate()
sc = spark.sparkContext
```

### 📌 개념 설명:

*   **SparkSession**: Spark SQL 및 DataFrame API 사용을 위한 진입점입니다. 최신 Spark에서 작업을 시작할 때 기본적으로 사용하는 객체입니다.
    
*   **SparkContext**: RDD(Resilient Distributed Dataset) 연산의 진입점입니다. PySpark에서 데이터를 병렬로 처리할 때 필요합니다.
    
*   **`.appName()`**: 실행 중인 Spark 애플리케이션에 이름을 부여합니다.
    

<br>

✅ 2. 숫자 데이터 생성 및 변환
-------------------

### 2-1. RDD 생성

```python
numbers = sc.parallelize(range(1, 21))
```

*   **`parallelize()`**: 일반 파이썬 리스트를 분산된 데이터 구조(RDD)로 변환합니다.
    
*   **`range(1, 21)`**: 1부터 20까지의 숫자 생성.
    

```python
print(numbers.collect())
```

*   **`collect()`**: RDD의 모든 데이터를 드라이버 프로그램으로 가져옵니다. 작은 데이터에서만 사용해야 합니다.
    

### 2-2. 데이터 변환 (map)

```python
doubled = numbers.map(lambda x: x * 2)
```

*   **`map()`**: 각 요소에 특정 연산을 적용하여 새로운 RDD를 생성합니다.
    
*   여기서는 모든 숫자에 `x * 2` 연산을 적용하여 2배로 만듭니다.
    

### 2-3. 조건 필터링 (filter)

```python
greater_than_10 = numbers.filter(lambda x: x > 10)
```

*   **`filter()`**: 조건에 맞는 요소만 남깁니다.
    
*   여기서는 10보다 큰 값만 남깁니다.
    

### 2-4. 개수 계산

```python
print(numbers.count())
print(greater_than_10.count())
```

*   **`count()`**: 전체 요소의 개수를 반환합니다.
    

<br>

✅ 3. 알파벳 문자열 데이터 변환
-------------------

### 3-1. 알파벳 리스트 생성

```python
alphabets = sc.parallelize(["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"])
```

*   문자열 리스트를 RDD로 변환합니다.
    

### 3-2. 문자열 연산

```python
repeated = alphabets.map(lambda x: x * 2)
```

*   각 문자를 두 번 반복한 문자열로 변환 (`"A" → "AA"`).
    

```python
after_E = alphabets.filter(lambda x: x > "E")
```

*   문자열 비교는 유니코드 순서를 따르며, `"E"`보다 사전 순으로 뒤에 있는 문자를 필터링합니다.
    

### 3-3. 소문자 변환

```python
lower_alphabets = alphabets.map(lambda x: x.lower())
```

*   문자열의 메서드 `.lower()`를 사용하여 대문자를 소문자로 변환합니다.
    

<br>

✅ 4. 랜덤 숫자 리스트 변환
-----------------

### 4-1. RDD 생성 및 제곱 연산

```python
random_numbers = sc.parallelize([3, 10, 5, 7, 1])
squared = random_numbers.map(lambda x: x * x)
```

*   각 숫자를 **자기 자신으로 곱하여 제곱**합니다 (`3 → 9`, `10 → 100`, ...).
    

### 4-2. 조건 필터링

```python
greater_than_10_sq = squared.filter(lambda x: x > 10)
```

*   제곱한 결과 중 `10`보다 큰 숫자만 필터링합니다.
    

### 4-3. 개수 출력

```python
print(greater_than_10_sq.count())
```

*   조건을 만족하는 요소의 개수를 출력합니다.
    
<br>

✅ 5. 전체 코드
-----------------


```python

# 데이터 생성 및 변환 실습 Answer 파일

from pyspark.sql import SparkSession

# SparkSession 생성
spark = SparkSession.builder.appName("Transformations").getOrCreate()
sc = spark.sparkContext

# 1. 버전 확인
# Spark version: 3.5.4
print("Spark version:", sc.version)

# 2. 숫자 데이터 생성 및 변환 연산
# 1~20까지 숫자 데이터 생성
numbers = sc.parallelize(range(1, 21))

# 생성된 데이터 확인
# [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]         
print(numbers.collect())

# 각 숫자를 2배 변환
# [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40]
doubled = numbers.map(lambda x: x * 2)
print(doubled.collect())

# 10보다 큰 숫자만 출력
# [11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
greater_than_10 = numbers.filter(lambda x: x > 10)
print(greater_than_10.collect())

# 1~20까지 생성된 숫자의 총 개수 확인
# 20
print(numbers.count())

# 10보다 큰 숫자의 총 개수 확인
# 10
print(greater_than_10.count())

# 3. 알파벳 문자열 데이터 변환 연산
alphabets = sc.parallelize(["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"])

# 생성된 알파벳 데이터 확인
# ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
print(alphabets.collect())

# 각 문자를 두 번 반복
# ['AA', 'BB', 'CC', 'DD', 'EE', 'FF', 'GG', 'HH', 'II', 'JJ']
repeated = alphabets.map(lambda x: x * 2)
print(repeated.collect())

# "E"보다 뒤에 있는 문자만 출력
# ['F', 'G', 'H', 'I', 'J']
after_E = alphabets.filter(lambda x: x > "E")
print(after_E.collect())

# "E"보다 뒤에 있는 문자의 총 개수 확인
# 5
print(after_E.count())

# 알파벳 데이터를 소문자로 변환
# ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
lower_alphabets = alphabets.map(lambda x: x.lower())
print(lower_alphabets.collect())

# 4. 랜덤 숫자 리스트 변환
random_numbers = sc.parallelize([3, 10, 5, 7, 1])

# 모든 숫자를 제곱
# [9, 100, 25, 49, 1]
squared = random_numbers.map(lambda x: x * x)
print(squared.collect())

# 제곱한 숫자의 값 중 10보다 큰 값만 출력
# [100, 25, 49]                                                                   
greater_than_10_sq = squared.filter(lambda x: x > 10)
print(greater_than_10_sq.collect())

# 10보다 큰 값의 총 개수 확인
# 3
print(greater_than_10_sq.count())
```

<br>

🧠 핵심 개념 요약
-----------

| 개념 | 설명 | 예시 함수 |
| --- | --- | --- |
| RDD | 분산된 데이터 셋 | `sc.parallelize()` |
| Transformation | 변환, 지연 평가됨 | `map()`, `filter()` |
| Action | 결과를 리턴하고 연산 실행 | `collect()`, `count()` |
| Lambda 함수 | 파이썬의 익명 함수 | `lambda x: x * 2` |
| 문자열 메서드 | `.lower()` → 소문자 변환 | `"A".lower()` → `"a"` |

<br>

✅ 실습을 통해 얻는 핵심 역량
-----------------

*   PySpark에서 **RDD 생성 및 연산 방식**을 익힘
    
*   `map`, `filter`, `count`와 같은 **핵심 Transformation & Action 사용법 습득**
    
*   숫자/문자/문자열 데이터를 다루는 다양한 실습 경험
    
*   **지연 평가(Lazy Evaluation)** 개념 간접 체험
    
*   **분산 처리의 기초** 감각 습득