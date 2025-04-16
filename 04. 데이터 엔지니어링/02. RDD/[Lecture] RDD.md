📘 RDD 정리 노트
============
```text
[Abstract]
Apache Spark의 핵심 추상화인 RDD(Resilient Distributed Dataset)는 대규모 데이터 처리의 효율성과 신뢰성을 보장하는 분산 데이터 구조입니다. RDD는 불변성(Immutable), 탄력성(Resilient), 타입 안정성(Type-safe), 지연 평가(Lazy Evaluation) 등의 특징을 갖추고 있으며, 정형 및 비정형 데이터를 모두 처리할 수 있습니다.​

RDD는 두 가지 주요 연산으로 구성됩니다: 변환(Transformations)과 액션(Actions). 변환 연산은 기존 RDD를 기반으로 새로운 RDD를 생성하며, 지연 평가되어 액션 연산이 호출될 때까지 실행되지 않습니다. 대표적인 변환 연산으로는 map(), flatMap(), filter(), groupByKey(), reduceByKey() 등이 있습니다. 액션 연산은 변환 연산을 실제로 실행하여 결과를 반환하거나 외부 저장소에 데이터를 저장합니다. 주요 액션 연산으로는 collect(), count(), reduce(), saveAsTextFile() 등이 있습니다.​

RDD는 다양한 방법으로 생성할 수 있습니다. 로컬 컬렉션을 RDD로 변환하는 parallelize() 메서드, 외부 파일에서 RDD를 생성하는 textFile() 메서드 등이 있으며, CSV나 JSON 파일을 읽어 DataFrame으로 변환한 후 RDD로 변환하는 방법도 있습니다.​

RDD의 변환 연산을 활용하여 데이터의 구조를 변경하거나 필터링, 집계 등의 작업을 수행할 수 있습니다. 예를 들어, map()을 사용하여 각 요소에 함수를 적용하거나, filter()를 사용하여 특정 조건을 만족하는 요소만 추출할 수 있습니다. 또한, groupByKey()와 reduceByKey()를 사용하여 키를 기준으로 데이터를 그룹화하거나 집계할 수 있습니다.​

액션 연산을 통해 변환된 RDD를 실제로 실행하여 결과를 얻거나 데이터를 저장할 수 있습니다. 예를 들어, collect()를 사용하여 RDD의 모든 요소를 드라이버 프로그램으로 가져오거나, saveAsTextFile()을 사용하여 RDD를 텍스트 파일로 저장할 수 있습니다.​

이러한 RDD의 개념과 연산들을 이해하고 활용함으로써, Apache Spark를 사용한 대규모 데이터 처리 및 분석 작업을 효율적으로 수행할 수 있습니다.
```

------------------


1\. RDD의 개념과 특징 이해
------------------

### RDD란?

**RDD(Resilient Distributed Dataset)** 는 Apache Spark의 핵심 데이터 구조로, 클러스터 내 여러 노드에 분산되어 저장되는 불변(immutable)한 데이터 컬렉션입니다. RDD는 병렬 처리를 지원하며, 데이터 손실 시 복구 가능한 특성을 가지고 있습니다.​

### RDD의 특징

#### 1\. 데이터의 추상화 (Data Abstraction)

RDD는 분산된 데이터를 추상화하여, 사용자가 복잡한 분산 처리 로직을 직접 다루지 않고도 데이터를 조작할 수 있게 해줍니다.​

#### 2\. 탄력성 (Resilient) & 불변성 (Immutable)

*   **불변성**: RDD는 생성 후 변경할 수 없으며, 변환 시 새로운 RDD를 생성합니다.
    
*   **탄력성**: RDD는 lineage 정보를 통해 데이터 손실 시 자동으로 복구할 수 있습니다.​
    

#### 3\. 타입 안정성 (Type-safe)

RDD는 강력한 타입 검사를 지원하여, 컴파일 시점에 오류를 발견할 수 있어 안정적인 코드 작성을 도와줍니다.​

#### 4\. 정형 & 비정형 데이터 처리

RDD는 텍스트, JSON, CSV 등 다양한 형식의 데이터를 처리할 수 있어, 정형 및 비정형 데이터 모두에 유연하게 대응합니다.    
​비정형 데이터 -> sc.textFile() 활용 / 정형 데이터 -> DataFrame 또는 RDD.map() 활용

#### 5\. 지연 평가 (Lazy Evaluation)

RDD의 변환 연산은 지연 평가되어, 실제로 액션 연산이 호출되기 전까지 실행되지 않습니다.     
이를 통해 최적화된 실행 계획을 수립할 수 있습니다.​

### Spark RDD란?

Spark에서 RDD는 기본 데이터 추상화로, 분산된 데이터를 효과적으로 처리하기 위한 다양한 기능을 제공합니다.​

#### 주요 구성 요소

*   **의존성 정보 (Lineage)**: RDD가 어떻게 생성되었는지를 추적하는 정보로, 장애 발생 시 복구에 사용됩니다.
    
*   **파티션 (Partition)**: RDD는 여러 파티션으로 나뉘어 클러스터의 노드에 분산 저장됩니다.
    
*   **연산 함수**: 각 파티션에 적용되는 함수로, 데이터를 처리하는 로직을 정의합니다.​
  
```python
from pyspark import SparkContext

sc = SparkContext("local", "LazyEvalExample")

# 1. 텍스트 데이터 로딩 -> Transformation
rdd = sc.parallelize(["apple", "banana", "spark", "data"])

# 2. 대문자로 바꾸기 -> Transformation
upper_rdd = rdd.map(lambda x: x.upper())

# 3. SPARK가 포함된 문자열만 필터링 -> Transformation
filtered_rdd = upper_rdd.filter(lambda x: "SPARK" in x)

# 지금까지는 아무것도 실행되지 않음!

# 4. 결과 확인(Action)
result = filtered_rdd.collect()
```

2\. RDD 생성 및 변환 학습
------------------

### 2.1 RDD 생성

#### 1\. 기존의 메모리 데이터를 RDD로 변환하는 방법

Spark에서는 로컬 컬렉션을 RDD로 변환하기 위해 `parallelize()` 메서드를 사용합니다.​[DATA & AI](https://ingu627.github.io/spark/spark_db18/?utm_source=chatgpt.com)

```python
data = [1, 2, 3, 4, 5]  # 로컬 리스트 생성
rdd = sc.parallelize(data)  # 리스트를 RDD로 병렬화
```

여기서 `sc`는 `SparkContext`를 의미하며, `parallelize()`는 로컬 데이터를 분산된 RDD로 변환합니다.​

#### 2\. 외부 파일(텍스트, CSV, JSON 등)에서 RDD를 생성하는 방법

Spark는 다양한 외부 파일 형식에서 RDD를 생성할 수 있습니다.​

*   **텍스트 파일**: `textFile()` 메서드를 사용하여 각 라인을 RDD의 요소로 읽어옵니다.​[DATA & AI](https://ingu627.github.io/spark/spark_db18/?utm_source=chatgpt.com)
    
    ```python
    rdd = sc.textFile("path/to/file.txt")  # 텍스트 파일을 RDD로 읽어옴 (한 줄씩 요소로 구성)
    ```
    
*   **CSV 파일**: `SparkSession`을 사용하여 DataFrame으로 읽은 후, `rdd` 메서드를 통해 RDD로 변환합니다.​[DATA & AI](https://ingu627.github.io/spark/spark_db18/?utm_source=chatgpt.com)
    
    ```python
    df = spark.read.option("header", True).csv("path/to/file.csv")  # 헤더가 있는 CSV 파일을 DataFrame으로 읽기
    rdd = df.rdd  # DataFrame을 RDD로 변환
    ```
    
*   **JSON 파일**: CSV와 유사하게 처리합니다.​
    
    ```python
    df = spark.read.json("path/to/file.json")  # JSON 파일을 DataFrame으로 읽기
    rdd = df.rdd  # DataFrame을 RDD로 변환
    ```
    

#### Parallelize()

`parallelize()`는 로컬 컬렉션을 RDD로 변환하는 데 사용됩니다.​

```python
data = ["apple", "banana", "cherry"]  # 문자열 리스트 생성
rdd = sc.parallelize(data)  # 리스트를 RDD로 병렬화
```

옵션으로 파티션 수를 지정할 수 있습니다.​[DATA & AI](https://ingu627.github.io/spark/spark_db18/?utm_source=chatgpt.com)

```python
rdd = sc.parallelize(data, numSlices=2)  # 데이터를 2개의 파티션으로 나누어 RDD 생성
```

#### sc.textFile()

`textFile()`은 외부 텍스트 파일을 RDD로 읽어옵니다.​

```python
rdd = sc.textFile("path/to/file.txt")  # 텍스트 파일을 RDD로 읽어옴 (각 줄이 하나의 요소)
```

이 메서드는 HDFS, 로컬 파일 시스템 등 다양한 파일 시스템을 지원합니다.​[제2의 개발공부](https://jineeblog.tistory.com/11?utm_source=chatgpt.com)

### 2.2 RDD 변환 (Transformations)

Spark RDD의 변환 연산은 기존 RDD를 변형하여 새로운 RDD를 생성하는 연산입니다. 이러한 변환은 지연 평가(Lazy Evaluation) 방식으로 동작하여, 실제로 액션 연산이 호출되기 전까지 실행되지 않습니다.​

#### MAP

`map()` 함수는 RDD의 각 요소에 주어진 함수를 적용하여 새로운 RDD를 생성합니다. 이 연산은 입력과 출력의 요소 수가 동일합니다.​

```python
rdd = sc.parallelize(range(1, 6))  # Python은 range(1, 6)으로 1~5 생성
mapped_rdd = rdd.map(lambda x: x * 2)
result = mapped_rdd.collect()
print(result)  # 출력: [2, 4, 6, 8, 10]
```

#### FLATMAP

`flatMap()` 함수는 각 입력 요소에 함수를 적용하고, 결과를 평탄화하여 새로운 RDD를 생성합니다. 주로 문자열을 단어로 분리할 때 사용됩니다.​

```python
rdd = sc.parallelize(["Hello World", "Apache Spark"])  # 문자열 리스트를 RDD로 생성
words_rdd = rdd.flatMap(lambda line: line.split(" "))  # 각 줄을 단어로 분리
result = words_rdd.collect()
print(result)  # 출력: ['Hello', 'World', 'Apache', 'Spark']
```

#### FILTER

`filter()` 함수는 주어진 조건을 만족하는 요소만을 포함하는 새로운 RDD를 생성합니다.​

```python
rdd = sc.parallelize(range(1, 11))  # 1부터 10까지 RDD 생성
even_numbers_rdd = rdd.filter(lambda x: x % 2 == 0)  # 짝수만 필터링
result = even_numbers_rdd.collect()
print(result)  # 출력: [2, 4, 6, 8, 10]
```

#### MAPPARTITIONS

`mapPartitions()` 함수는 각 파티션에 함수를 적용하여 새로운 RDD를 생성합니다.     
이 연산은 파티션 단위로 작업을 수행하므로, `map()`보다 효율적일 수 있지만, 파티션 크기가 크다면 실행이 안될 수도 있다.

```python
rdd = sc.parallelize(range(1, 10), 3)  # 1부터 9까지 데이터를 3개의 파티션으로 나눠 RDD 생성
partition_mapped_rdd = rdd.mapPartitions(lambda iter: map(lambda x: x * 2, iter))  # 파티션 단위로 2배 처리
result = partition_mapped_rdd.collect()
print(result)  # 출력: [2, 4, 6, 8, 10, 12, 14, 16, 18]
```

#### MAPPARTITIONS WITH INDEX
- 각 파티션에 대해 파티션 인덱스와 해당 파티션의 이터레이터를 인자로 받아 연산을 수행하는 변환 함수입니다.
- 결과는 새로운 RDD로 반환됩니다.
- 일반 mapPartitions()와 달리, 어느 파티션에서 수행되는지 추적할 수 있습니다.

```python
rdd = sc.parallelize(["apple", "banana", "cherry", "date", "eggfruit"], 3)  # 3개의 파티션으로 나눔

def show_partition_index(index, iterator):
    return [f"Partition {index}: {item}" for item in iterator]

partitioned_rdd = rdd.mapPartitionsWithIndex(show_partition_index)
result = partitioned_rdd.collect()

print(result)
```

#### KEYBY

`keyBy()` 함수는 RDD의 각 요소를 키-값 쌍으로 변환하여 Pair RDD를 생성합니다.​

```python
# 글자의 길이로 INDEX를 생성
rdd = sc.parallelize(["apple", "banana", "cherry"])  # 문자열 리스트를 RDD로 생성
keyed_rdd = rdd.keyBy(lambda word: len(word))  # 단어 길이를 키로 지정
result = keyed_rdd.collect()
print(result)  # 출력: [(5, 'apple'), (6, 'banana'), (6, 'cherry')]

# 글자의 앞글자로 INDEX를 생성
rdd = sc.parallelize(["apple", "banana", "cherry"])  # 문자열 리스트를 RDD로 생성
keyed_rdd = rdd.keyBy(lambda word: word[0])  # 단어 길이를 키로 지정
result = keyed_rdd.collect()
print(result)  # 출력: [('a', 'apple'), ('b', 'banana'), ('c', 'cherry')]
```

#### JOIN

`join()` 함수는 두 개의 RDD를 키를 기준으로 조인하여 새로운 RDD를 생성합니다.​

```python
rdd1 = sc.parallelize([("a", 1), ("b", 2)])  # 첫 번째 (key, value) RDD
rdd2 = sc.parallelize([("a", 3), ("b", 4), ("a", 5)])  # 두 번째 (key, value) RDD
joined_rdd = rdd1.join(rdd2)  # 키를 기준으로 조인
result = joined_rdd.collect()
print(result)  # 출력: [('a', (1, 3)), ('b', (2, 4)), ('a', (1, 5))]
```

#### GROUPBY

`groupBy()` 함수는 주어진 함수를 기준으로 데이터를 그룹화하여 새로운 RDD를 생성합니다.​

```python
rdd = sc.parallelize(range(1, 6))  # 1부터 5까지 RDD 생성
grouped_rdd = rdd.groupBy(lambda x: x % 2)  # 홀수/짝수 기준으로 그룹화
result = {k: list(v) for k, v in grouped_rdd.collect()}
print(result)  # 출력: {1: [1, 3, 5], 0: [2, 4]}
```

#### GROUPBYKEY

- `groupByKey()` 함수는 키를 기준으로 값을 그룹화하여 새로운 RDD를 생성합니다.​
- `groupBy()`보다 `groupByKey()`를 권장
```python
rdd = sc.parallelize([("a", 1), ("b", 2), ("a", 3)])  # (key, value) 형태의 RDD 생성
grouped_rdd = rdd.groupByKey()  # 키를 기준으로 값들을 그룹화
result = {k: list(v) for k, v in grouped_rdd.collect()}
print(result)  # 출력: {'a': [1, 3], 'b': [2]}
```

`groupByKey()`는 모든 값을 셔플링하여 메모리 사용량이 많을 수 있으므로, 가능한 경우 `reduceByKey()`를 사용하는 것이 좋습니다.​

#### REDUCEBYKEY

`reduceByKey()` 함수는 키를 기준으로 값을 병합하여 새로운 RDD를 생성합니다.​

```python
rdd = sc.parallelize([("a", 1), ("b", 2), ("a", 3)])  # (key, value) 형태의 RDD 생성
reduced_rdd = rdd.reduceByKey(lambda a, b: a + b)  # 키별로 값을 합산
result = reduced_rdd.collect()
print(result)  # 출력: [('a', 4), ('b', 2)]
```

`reduceByKey()`는 로컬에서 먼저 병합을 수행한 후 셔플링하므로, `groupByKey()`보다 효율적입니다.​


#### 🧮 Word Count 예제: `groupByKey()` vs `reduceByKey()`
---------------------------------------------------

##### 1\. `groupByKey()`를 이용한 Word Count

`groupByKey()`는 동일한 키를 가진 모든 값을 그룹화하여 `(key, Iterable[values])` 형태의 RDD를 생성합니다.​[Apache Spark](https://spark.apache.org/docs/latest/rdd-programming-guide.html?utm_source=chatgpt.com)

```python
# 텍스트 파일을 읽고 각 줄을 단어로 분리
lines = sc.textFile("path/to/file.txt")
words = lines.flatMap(lambda line: line.split())

# 각 단어를 (word, 1) 형태로 매핑
word_pairs = words.map(lambda word: (word, 1))

# 단어별로 값을 그룹화
grouped = word_pairs.groupByKey()

# 각 단어의 총 출현 횟수를 계산
word_counts = grouped.map(lambda word_group: (word_group[0], sum(word_group[1])))

# 결과 출력
for word, count in word_counts.collect():
    print(f"{word}: {count}")
```

**주의사항**:

*   `groupByKey()`는 모든 값을 셔플링하여 네트워크를 통해 이동시키므로, 데이터 양이 많을 경우 성능 저하와 메모리 부족 문제가 발생할 수 있습니다.​
    

##### 2\. `reduceByKey()`를 이용한 Word Count

`reduceByKey()`는 동일한 키를 가진 값을 지정된 함수로 병합하여 `(key, aggregated_value)` 형태의 RDD를 생성합니다.​[Spark By {Examples}+2Apache Spark+2Databricks Community+2](https://spark.apache.org/docs/latest/rdd-programming-guide.html?utm_source=chatgpt.com)

```python
# 텍스트 파일을 읽고 각 줄을 단어로 분리
lines = sc.textFile("path/to/file.txt")
words = lines.flatMap(lambda line: line.split())

# 각 단어를 (word, 1) 형태로 매핑
word_pairs = words.map(lambda word: (word, 1))

# 단어별로 값을 병합하여 총 출현 횟수 계산
word_counts = word_pairs.reduceByKey(lambda a, b: a + b)

# 결과 출력
for word, count in word_counts.collect():
    print(f"{word}: {count}")
```

**장점**:

*   `reduceByKey()`는 각 파티션 내에서 로컬 병합을 수행한 후 셔플링하므로, 네트워크 I/O를 줄이고 성능을 향상시킵니다.​
    


##### ⚖️ `groupByKey()` vs `reduceByKey()` 비교
---------------------------------------

| 항목          | `groupByKey()`                                          | `reduceByKey()`                                |
| ------------- | ------------------------------------------------------- | ---------------------------------------------- |
| 연산 방식     | 키를 기준으로 모든 값을 그룹화하여 Iterable 생성        | 키를 기준으로 값을 병합하여 단일 값 생성       |
| 셔플링        | 모든 값을 셔플링하여 네트워크 부하 증가                 | 로컬 병합 후 최소한의 셔플링 수행              |
| 메모리 사용량 | 그룹화된 값이 많을 경우 메모리 사용량 증가              | 병합된 단일 값만 유지하므로 메모리 사용량 감소 |
| 사용 시기     | 모든 값을 유지해야 하는 경우 (예: 평균, 중간값 계산 등) | 합계, 최대값 등 병합 가능한 연산에 적합        |
| 성능          | 데이터 양이 많을 경우 성능 저하 가능                    | 대규모 데이터 처리에 효율적                    |

* * *

##### ✅ 결론
----

*   단어 수를 세는 등의 집계 작업에는 `reduceByKey()`를 사용하는 것이 성능과 자원 효율성 측면에서 유리합니다.
    
*   모든 값을 유지해야 하는 특수한 경우에는 `groupByKey()`를 사용할 수 있지만, 데이터 양이 많을 경우 주의가 필요합니다.​


#### UNION

**정의**: 두 개의 RDD를 결합하여 하나의 RDD로 만듭니다. 중복된 요소도 포함됩니다.​

**사용 예시**:

```python
rdd1 = sc.parallelize(["apple", "banana"])  # 첫 번째 RDD 생성
rdd2 = sc.parallelize(["banana", "cherry"])  # 두 번째 RDD 생성
union_rdd = rdd1.union(rdd2)  # 두 RDD를 합침 (중복 허용)
result = union_rdd.collect()
print(result)  # 출력: ['apple', 'banana', 'banana', 'cherry']
```

**특징**:

*   입력 RDD들의 데이터 타입이 동일해야 합니다.
    
*   중복된 요소를 제거하지 않습니다. 중복 제거를 원한다면 `distinct()`를 추가로 사용해야 합니다.​
    


#### DISTINCT

**정의**: RDD에서 중복된 요소를 제거하여 고유한 요소만 포함하는 새로운 RDD를 생성합니다.​

**사용 예시**:

```python
rdd = sc.parallelize(["apple", "banana", "apple", "cherry"])  # 중복된 요소 포함 RDD 생성
distinct_rdd = rdd.distinct()  # 중복 제거
result = distinct_rdd.collect()
print(result)  # 출력: ['apple', 'banana', 'cherry']
```

**특징**:

*   모든 데이터를 셔플링하여 중복을 제거하므로, 대규모 데이터셋에서는 성능에 영향을 줄 수 있습니다.
    
*   필요한 경우 파티션 수를 지정할 수 있습니다: `rdd.distinct(numPartitions)`​[Stack Overflow](https://stackoverflow.com/questions/31610971/spark-repartition-vs-coalesce?utm_source=chatgpt.com)
    

#### COALESCE

**정의**: RDD의 파티션 수를 줄여서 새로운 RDD를 생성합니다. 주로 출력 파일 수를 줄이거나 리소스를 절약할 때 사용됩니다.​

**사용 예시**:

```python
rdd = sc.parallelize(range(1, 11), 4)  # 1부터 10까지 데이터를 4개의 파티션으로 분할하여 RDD 생성
coalesced_rdd = rdd.coalesce(2)  # 파티션 수를 2개로 줄임
result = coalesced_rdd.getNumPartitions()
print(result)  # 출력: 2
```

**특징**:

*   기존 파티션을 병합하여 새로운 파티션을 생성하므로, 셔플링이 발생하지 않아 효율적입니다.
    
*   기본적으로 셔플링을 수행하지 않지만, `shuffle = true` 옵션을 사용하면 셔플링을 통해 더 균등한 파티션 분배가 가능합니다.​
    
#### REPARTITION
*   **기능**: 파티션 수를 늘리거나 줄일 수 있으며, 내부적으로 항상 **전체 셔플링**을 발생시킴.
    
*   **용도**: 데이터 분산이 불균형하거나 파티션 수가 너무 적을 때, 병렬성을 높이고 싶을 때 사용.

```python
rdd = sc.parallelize(range(1, 11), 2)  # 초기 2개 파티션
reparted_rdd = rdd.repartition(4)     # 4개로 재분배 (전체 셔플 발생)
print(reparted_rdd.getNumPartitions())  # 출력: 4
```

#### 📌 `repartition()` vs `coalesce()` 비교 요약
----------------------------------------

| 항목               | `repartition()`                            | `coalesce()`                                |
| ------------------ | ------------------------------------------ | ------------------------------------------- |
| 목적               | 파티션 수 **늘리기 또는 줄이기** 모두 가능 | 파티션 수 **줄이기 전용**                   |
| 셔플 발생 여부     | 항상 셔플 발생 (모든 데이터를 재분배)      | 기본적으로 **셔플 없음** (선택적 발생 가능) |
| 데이터 재배치 방식 | **전체 셔플링**하여 균등 분산              | 일부 파티션만 병합 (데이터 쏠림 가능)       |
| 사용 예시          | 작업 병렬성 증가 또는 고르게 나눌 때       | 작업 단순화, 출력 파일 수 줄일 때           |
| 성능               | 느릴 수 있음 (셔플 비용 큼)                | 상대적으로 빠름 (셔플 없이 처리 가능)       |

##### ✅ 실전 팁
------

*   `repartition()`은 **정렬 작업 전** 데이터 고른 분산이 중요할 때 유용
    
*   `coalesce()`는 **출력 최적화**(예: 하나의 파일로 저장 등) 시 자주 사용

#### PARTITIONBY

**정의**: Pair RDD를 특정 파티셔너에 따라 재분배하여 새로운 RDD를 생성합니다. 주로 키 기반 연산의 성능을 향상시키기 위해 사용됩니다.​

**사용 예시**:

```python
pair_rdd = sc.parallelize([("apple", 1), ("banana", 2), ("cherry", 3)])  # (key, value) 형태의 RDD 생성
partitioned_rdd = pair_rdd.partitionBy(2, lambda key: hash(key))  # 해시 파티셔너로 2개의 파티션 분배
result = partitioned_rdd.getNumPartitions()
print(result)  # 출력: 2
```

**특징**:

*   `HashPartitioner`나 `RangePartitioner`와 같은 파티셔너를 사용하여 데이터를 분배합니다.
    
*   `partitionBy()`를 사용하면 이후의 `groupByKey()`, `reduceByKey()` 등의 연산에서 셔플링을 줄일 수 있어 성능이 향상됩니다.
    
*   `partitionBy()`는 Pair RDD에만 적용 가능합니다.​

### 2.3 RSS Fundamentals

#### Sample

`sample()` 함수는 RDD에서 무작위로 샘플을 추출하여 새로운 RDD를 생성합니다.     
이 함수는 데이터의 일부를 분석하거나 테스트할 때 유용합니다.​ 

```python
# withReplacement: 복원 추출 여부 (True/False)
# fraction: 전체 데이터에서 샘플링할 비율 (0.0 ~ 1.0)
# seed: 난수 생성 시드 값
sampled_rdd = rdd.sample(withReplacement=False, fraction=0.1, seed=42)
```

#### Collect

`collect()` 함수는 RDD의 모든 요소를 드라이버 프로그램으로 가져와 리스트로 반환합니다. 소규모 데이터셋에서 결과를 확인할 때 사용됩니다.​

```python
data = rdd.collect()
```

**주의**: 대규모 RDD에 대해 `collect()`를 사용하면 메모리 부족이 발생할 수 있습니다.​

#### CountByKey

`countByKey()` 함수는 (K, V) 형태의 RDD에서 각 키에 대한 값의 개수를 계산하여 딕셔너리로 반환합니다.​

```python
rdd = sc.parallelize([("a", 1), ("b", 2), ("a", 3)])
counts = rdd.countByKey()
# 결과: {'a': 2, 'b': 1}
```

#### Reduce

`reduce()` 함수는 RDD의 요소들을 지정된 이항 함수로 집계하여 단일 결과를 반환합니다.​

```python
rdd = sc.parallelize([1, 2, 3, 4])
total = rdd.reduce(lambda x, y: x + y)
# 결과: 10
```

#### Sum

`sum()` 함수는 RDD의 모든 숫자 요소를 합산하여 반환합니다.​

```python
total = rdd.sum()
```

#### Max

`max()` 함수는 RDD에서 최대값을 반환합니다.​

```python
maximum = rdd.max()
```

#### Mean

`mean()` 함수는 RDD의 평균값을 계산하여 반환합니다.​

```python
average = rdd.mean()
```

#### Stdev

`stdev()` 함수는 RDD의 표준편차를 계산하여 반환합니다.​

```python
std_deviation = rdd.stdev()
```

### 2.4 RDD Action
RDD의 액션 연산은 지연 평가된 변환 연산들을 실제로 실행하여 결과를 반환하거나 외부 저장소에 저장하는 연산입니다.​
#### ACTIONS
##### 1\. `collect()`

RDD의 모든 요소를 드라이버 프로그램으로 가져와 리스트로 반환합니다.​

```python
data = rdd.collect()
```

**주의**: 대규모 RDD에 대해 `collect()`를 사용하면 메모리 부족이 발생할 수 있습니다.​

##### 2\. `count()`

RDD의 요소 개수를 반환합니다.​[Apache Spark](https://spark.apache.org/docs/latest/api/python/reference/api/pyspark.RDD.countByKey.html?utm_source=chatgpt.com)

```python
num_elements = rdd.count()
```

##### 3\. `first()`

RDD의 첫 번째 요소를 반환합니다.​

```python
first_element = rdd.first()
```

##### 4\. `take(n)`

RDD의 처음 `n`개의 요소를 리스트로 반환합니다.​

```python
first_n = rdd.take(5)
```

##### 5\. `takeSample(withReplacement, num, [seed])`

RDD에서 무작위로 샘플을 추출하여 리스트로 반환합니다.​

```python
sample = rdd.takeSample(False, 3, seed=42)
```

##### 6\. `reduce(func)`

RDD의 요소들을 지정된 이항 함수로 집계하여 단일 결과를 반환합니다.​

```python
total = rdd.reduce(lambda x, y: x + y)
```

##### 7\. `foreach(func)`

RDD의 각 요소에 함수를 적용합니다. 주로 외부 시스템과의 연동이나 로그 출력 등에 사용됩니다.​[Apache Spark+1Learn R, Python & Data Science Online+1](https://spark.apache.org/docs/latest/rdd-programming-guide.html?utm_source=chatgpt.com)

```python
rdd.foreach(lambda x: print(x))
```

#### RDD 데이터 불러오기와 저장하기
RDD의 데이터를 외부 저장소에 저장할 수 있는 액션 연산입니다.​

##### 1\. `saveAsTextFile(path)`

RDD를 텍스트 파일로 저장합니다. 각 요소는 문자열로 변환되어 한 줄씩 저장됩니다.​

```python
rdd.saveAsTextFile("output/path")
```

**특징**:

*   디렉토리 형태로 저장되며, 각 파티션은 별도의 파일로 저장됩니다.
    
*   압축 코덱을 지정하여 저장할 수 있습니다.​
    

##### 2. `saveAsSequenceFile(path)`

(키, 값) 형태의 RDD를 Hadoop SequenceFile 형식으로 저장합니다.​[Stack Overflow+2george-jen.gitbook.io+2Medium+2](https://george-jen.gitbook.io/data-science-and-apache-spark/rdd-action-functions?utm_source=chatgpt.com)

```python
pair_rdd.saveAsSequenceFile("output/sequence")
```

**주의**: RDD의 요소가 (키, 값) 형태여야 하며, 키와 값은 Hadoop의 Writable 인터페이스를 구현해야 합니다.​[george-jen.gitbook.io](https://george-jen.gitbook.io/data-science-and-apache-spark/rdd-action-functions?utm_source=chatgpt.com)

##### 3. `saveAsObjectFile(path)`

RDD의 요소를 Java 직렬화를 사용하여 객체 파일로 저장합니다.​

```python
rdd.saveAsObjectFile("output/object")
```

**특징**:

*   Java와 Scala에서 지원되며, Python에서는 사용이 제한적입니다.
    
*   저장된 파일은 `SparkContext.objectFile()`을 사용하여 다시 읽을 수 있습니다.​[Stack Overflow+2Medium+2george-jen.gitbook.io+2](https://medium.com/%40singhsameer121295/exploring-pyspark-rdds-saving-data-in-different-file-formats-6fba8c07d45c?utm_source=chatgpt.com)[george-jen.gitbook.io](https://george-jen.gitbook.io/data-science-and-apache-spark/rdd-action-functions?utm_source=chatgpt.com)
    