📘 금융 텍스트 데이터 로드 및 탐색
=========================

> 이 문서는 PySpark를 사용해 텍스트 파일을 불러오고, 데이터를 탐색 및 변환하는 실습 과정을 단계별로 설명한 자료입니다. 비전공자도 Spark 개념을 쉽게 이해할 수 있도록 구성하였습니다.

* * *

✅ 1. 환경 설정
----------

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("TextDataAnalysis").getOrCreate()
sc = spark.sparkContext
```

### 💡 개념 설명

*   **SparkSession**: Spark 애플리케이션의 시작점입니다. DataFrame이나 SQL 연산에 사용됩니다.
    
*   **SparkContext**: 저수준 API인 RDD(Resilient Distributed Dataset)를 제어하기 위한 진입점입니다.
    
*   **`.appName()`**: 애플리케이션의 이름을 지정합니다. 로그나 UI에서 표시됩니다.
    

* * *

✅ 2. 텍스트 파일 로드
--------------

```python
text_data = sc.textFile("../data/test_1.txt")
```

*   **`textFile()`**: 텍스트 파일을 한 줄씩 읽어 RDD로 변환합니다.
    
*   각 줄은 하나의 문자열(string)로 이루어져 있으며, RDD의 한 요소가 됩니다.
    

* * *

✅ 3. 전체 데이터 확인
--------------

```python
print(text_data.collect())
```

*   **`collect()`**: 전체 RDD 데이터를 드라이버 프로그램으로 가져옵니다.
    
*   작은 데이터셋에서만 사용해야 하며, 출력 시 리스트 형태로 반환됩니다.
    

### 📝 예시 출력

```text
[
 'The world’s most valuable resource is no longer oil, but data.',
 'Big Data and AI are transforming industries worldwide.',
 'Companies are investing heavily in real-time analytics.'
]
```

* * *

✅ 4. 줄 수 세기 (행 개수)
------------------

```python
print("전체 줄 개수:", text_data.count())
```

*   **`count()`**: 전체 RDD 요소(=줄)의 개수를 계산합니다.
    
*   예시 데이터는 3줄이므로 출력 결과는 `3`.
    

* * *

✅ 5. 특정 단어가 포함된 줄 필터링
---------------------

```python
contains_data = text_data.filter(lambda line: 'data' in line.lower())
```

### 💡 개념 설명

*   **`filter()`**: 조건에 해당하는 데이터만 걸러냅니다.
    
*   여기서는 각 줄을 모두 소문자로 바꾼 뒤, `'data'`라는 단어가 포함된 경우만 남깁니다.
    
*   **`in` 연산자**는 문자열 포함 여부를 확인합니다.
    

```python
print(contains_data.collect())
print("전체 줄 개수:", contains_data.count())
```

*   필터링된 줄만 출력되고, 몇 줄인지도 함께 확인합니다.
    

* * *

✅ 6. 대소문자 변환
------------

### 대문자로 변환

```python
upper_case_data = text_data.map(lambda line: line.upper())
print(upper_case_data.collect())
```

*   **`map()`**: RDD의 각 요소에 함수를 적용해 새로운 RDD를 생성합니다.
    
*   **`.upper()`**: 문자열을 모두 대문자로 바꾸는 파이썬 문자열 함수입니다.
    

### 소문자로 변환

```python
lower_case_data = text_data.map(lambda line: line.lower())
print(lower_case_data.collect())
```

*   **`.lower()`**: 문자열을 모두 소문자로 변환합니다.
    

* * *

✅ 7. 파티션 개수 확인 및 재분할
--------------------

```python
print("기본 파티션 개수:", text_data.getNumPartitions())
```

*   **`getNumPartitions()`**: RDD가 분산되어 있는 파티션의 수를 알려줍니다.
    
*   Spark는 데이터를 자동으로 나누어 여러 컴퓨터나 CPU 코어에서 병렬 처리할 수 있도록 합니다.
    
*   기본적으로는 실행 환경에 따라 파티션 수가 정해집니다 (예: 2개).
    

* * *

### 파티션 수 재설정

```python
repartitioned_data = text_data.repartition(4)
print("변경된 파티션 개수:", repartitioned_data.getNumPartitions())
```

*   **`repartition(n)`**: 파티션 수를 강제로 변경합니다.
    
*   예를 들어, 데이터를 4개의 파티션으로 나누면 더 많은 병렬 처리가 가능해질 수 있습니다.
    
*   **주의**: 너무 많은 파티션은 오히려 성능을 저하시킬 수 있으므로 적절한 수 조정이 중요합니다.
    
* * *

✅ 8. 전체 코드
--------------------
```python
from pyspark.sql import SparkSession

# SparkSession 생성
spark = SparkSession.builder.appName("TextDataAnalysis").getOrCreate()
sc = spark.sparkContext

# 텍스트 파일 로드
text_data = sc.textFile("../data/test_1.txt")

# 전체 텍스트 출력
# ['The world’s most valuable resource is no longer oil, but data.', 
#  'Big Data and AI are transforming industries worldwide.', 
#  'Companies are investing heavily in real-time analytics.']
print(text_data.collect())

# 줄 수 출력
# 전체 줄 개수: 3
print("전체 줄 개수:", text_data.count())

# 'data'가 포함된 문장 필터링
# ['The world’s most valuable resource is no longer oil, but data.', 
#  'Big Data and AI are transforming industries worldwide.']
contains_data = text_data.filter(lambda line: 'data' in line.lower())
print(contains_data.collect())

# 포함된 줄 수 출력
# 전체 줄 개수: 2
print("전체 줄 개수:", contains_data.count())

# 대문자로 변환
# ['THE WORLD’S MOST VALUABLE RESOURCE IS NO LONGER OIL, BUT DATA.', 
#  'BIG DATA AND AI ARE TRANSFORMING INDUSTRIES WORLDWIDE.', 
#  'COMPANIES ARE INVESTING HEAVILY IN REAL-TIME ANALYTICS.']
upper_case_data = text_data.map(lambda line: line.upper())
print(upper_case_data.collect())

# 소문자로 변환
# ['the world’s most valuable resource is no longer oil, but data.', 
#  'big data and ai are transforming industries worldwide.', 
#  'companies are investing heavily in real-time analytics.']
lower_case_data = text_data.map(lambda line: line.lower())
print(lower_case_data.collect())

# 기본 파티션 개수 확인
# 기본 파티션 개수: 2
print("기본 파티션 개수:", text_data.getNumPartitions())

# 파티션 4개로 재설정 후 확인
# 변경된 파티션 개수: 4
repartitioned_data = text_data.repartition(4)
print("변경된 파티션 개수:", repartitioned_data.getNumPartitions())
```
* * *

📌 주요 개념 요약
-----------

| 개념 | 설명 | 관련 함수 |
| --- | --- | --- |
| **RDD** | 분산된 데이터 집합 | `sc.textFile()`, `map()`, `filter()` |
| **Transformation** | 새로운 RDD 생성. 지연 평가됨 | `map()`, `filter()`, `repartition()` |
| **Action** | 실제 결과 반환, 실행 트리거 | `count()`, `collect()` |
| **lambda 함수** | 익명 함수 정의 문법 | `lambda x: x.upper()` |
| **대소문자 처리** | 문자열 메서드 사용 | `.upper()`, `.lower()` |
| **파티셔닝** | 데이터를 나눠 병렬 처리 | `getNumPartitions()`, `repartition()` |

* * *

🧠 실습을 통해 얻는 역량
---------------

*   텍스트 파일을 RDD로 불러오는 방법 학습
    
*   `filter`, `map`, `count` 등의 기본 RDD 연산 익히기
    
*   문자열 처리 (대소문자 변환)와 조건 필터링 실습
    
*   파티셔닝 개념과 병렬 처리 감각 익히기
