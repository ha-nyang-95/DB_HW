📘 RDD 연산 최적화 실습 정리본
====================

✨ 실습 목표
-------

*   Spark RDD에서의 `map()`, `filter()`, `flatMap()`, `mapPartitions()` 연산을 비교한다.
    
*   동일한 결과를 만드는 여러 연산 방식의 **성능 차이**를 직접 체감한다.
    
*   `mapPartitions()`과 같은 고급 연산의 **효율성**을 이해한다.
    

* * *

📌 1. SparkContext 생성
---------------------

```python
from pyspark import SparkContext
import time
sc = SparkContext("local", "RDDOptimization")
```

*   **SparkContext**는 Spark 애플리케이션을 시작하는 핵심 객체이며,
    
*   `"local"`은 로컬 머신에서 실행함을 의미하고,
    
*   `"RDDOptimization"`은 애플리케이션 이름이다.
    

* * *

📌 2. RDD 생성
------------

```python
num_partitions = 8
rdd = sc.parallelize(range(1, 1000001), num_partitions)
```

*   `parallelize(data, num_partitions)`: 데이터를 RDD로 만들고 **8개의 파티션**으로 나눔.
    
*   여기서는 **1부터 1,000,000까지** 숫자를 가진 RDD를 생성함.
    

* * *

📌 3. 시간 측정 함수
--------------

```python
def measure_time(fn):
    start = time.time()
    result = fn()
    end = time.time()
    return result, end - start
```

*   어떤 연산 함수 `fn`을 실행하고 **걸린 시간**을 측정해서 반환하는 유틸 함수.
    

* * *

📌 4. map + filter 방식
---------------------

```python
rdd.filter(lambda x: x % 2 == 0).map(lambda x: x * 2).collect()
```

### ✅ 동작 설명

*   먼저 `filter()`로 **짝수만 필터링** → 약 500,000개
    
*   이후 `map()`으로 **2배 연산** 수행
    
*   `.collect()`로 결과를 **드라이버로 가져옴**
    

### 🔍 결과 예시

```python
[map + filter] 개수: 500000
[map + filter] 샘플: [4, 8, 12, 16, 20]
[map + filter] 시간: 1.3814 초
```

### 📌 비효율적인 이유

*   `filter()`와 `map()`을 **별도로 실행** → 연산 오버헤드 발생
    
*   각 요소에 대해 두 번의 함수 호출이 필요함 (함수 호출 비용)
    

* * *

📌 5. flatMap 방식
----------------

```python
rdd.flatMap(lambda x: [x * 2] if x % 2 == 0 else []).collect()
```

### ✅ 동작 설명

*   한 번의 연산으로 `짝수이면 [x*2]`, 홀수이면 빈 리스트 반환
    
*   결과적으로 짝수만 걸러지고 2배 처리된 값만 남음
    
*   `map + filter`를 **한 줄로 통합**한 셈
    

### 🔍 결과 예시

```python
[flatMap] 개수: 500000
[flatMap] 샘플: [4, 8, 12, 16, 20]
[flatMap] 시간: 0.8412 초
```

### 📌 장점

*   함수 호출이 **1회로 줄어듦**
    
*   조건 분기와 변환을 **동시에 수행**
    
*   처리 속도 개선
    

* * *

📌 6. mapPartitions 방식
----------------------

```python
def transform_partition(iterator):
    return (x * 2 for x in iterator if x % 2 == 0)

rdd.mapPartitions(transform_partition).collect()
```

### ✅ 동작 설명

*   **각 파티션 단위로** 데이터를 처리함.
    
*   매 파티션마다 반복자(`iterator`)가 주어지며,
    
*   그 안에서 짝수를 필터링하고 2배 처리된 값만 반환.
    

### 🔍 결과 예시

```python
[mapPartitions] 개수: 500000
[mapPartitions] 샘플: [4, 8, 12, 16, 20]
[mapPartitions] 시간: 0.7741 초
```

### 📌 가장 효율적인 이유

*   **파티션 단위로 연산을 수행**하므로, 매 요소마다 함수 호출하는 `map`보다 효율적
    
*   메모리 사용과 CPU 호출이 감소 → 속도 개선
    

* * *

📌 7. 전체 코드
----------------------

```python
from pyspark import SparkContext
import time
sc = SparkContext("local", "RDDOptimization")

# 1. 파티션 개수 지정
num_partitions = 8

# 2. 1~1,000,000까지의 숫자 데이터를 포함하는 RDD 생성
rdd = sc.parallelize(range(1, 1000001), num_partitions)

# 3. 수행 시간 측정 함수 정의
def measure_time(fn):
    start = time.time()
    result = fn()
    end = time.time()
    return result, end - start

# 4. map+filter 연산
# [map + filter] 개수: 500000                                                     
# [map + filter] 샘플: [4, 8, 12, 16, 20]
# [map + filter] 시간: 1.3814 초
map_filter_result, t1 = measure_time(lambda: rdd.filter(lambda x: x % 2 == 0).map(lambda x: x * 2).collect())
print("[map + filter] 개수:", len(map_filter_result))
print("[map + filter] 샘플:", map_filter_result[:5])
print("[map + filter] 시간:", round(t1, 4), "초")

# 5. flatMap 연산
# [flatMap] 개수: 500000                                                          
# [flatMap] 샘플: [4, 8, 12, 16, 20]
# [flatMap] 시간: 0.8412 초
flatmap_result, t2 = measure_time(lambda: rdd.flatMap(lambda x: [x * 2] if x % 2 == 0 else []).collect())
print("[flatMap] 개수:", len(flatmap_result))
print("[flatMap] 샘플:", flatmap_result[:5])
print("[flatMap] 시간:", round(t2, 4), "초")

# 6. mapPartitions 연산
# [mapPartitions] 개수: 500000                                                    
# [mapPartitions] 샘플: [4, 8, 12, 16, 20]
# [mapPartitions] 시간: 0.7741 초
def transform_partition(iterator):
    return (x * 2 for x in iterator if x % 2 == 0)

mappart_result, t3 = measure_time(lambda: rdd.mapPartitions(transform_partition).collect())
print("[mapPartitions] 개수:", len(mappart_result))
print("[mapPartitions] 샘플:", mappart_result[:5])
print("[mapPartitions] 시간:", round(t3, 4), "초")
```
* * *

📊 성능 비교 요약표
------------

| 연산 방식       | 처리 방식                   | 함수 호출 수 | 장점              | 단점                       | 소요 시간 (예시) |
| --------------- | --------------------------- | ------------ | ----------------- | -------------------------- | ---------------- |
| `map + filter`  | 요소 단위로 2단계 처리      | 2회/요소     | 코드가 직관적     | 느림, 비효율적             | 1.38초           |
| `flatMap`       | 요소 단위로 1단계 통합 처리 | 1회/요소     | 효율적, 빠름      | 가독성이 살짝 낮을 수 있음 | 0.84초           |
| `mapPartitions` | 파티션 단위로 일괄 처리     | 1회/파티션   | 가장 빠름, 고성능 | 복잡한 로직 구현 시 주의   | 0.77초           |

* * *

🧠 핵심 개념 요약
-----------

| 용어                | 설명                                                          |
| ------------------- | ------------------------------------------------------------- |
| **filter()**        | 조건을 만족하는 요소만 남기는 연산                            |
| **map()**           | 각 요소에 대해 변환을 적용하는 연산                           |
| **flatMap()**       | 1:N 매핑이 가능한 map + filter 조합형 연산                    |
| **mapPartitions()** | 파티션 단위로 데이터를 처리하는 고성능 연산                   |
| **collect()**       | 전체 데이터를 드라이버로 수집 (주의: 메모리 초과 가능성 있음) |

* * *

✅ 실습을 통해 배운 점
-------------

*   **같은 작업이라도 연산 방식에 따라 성능 차이**가 크게 발생함.
    
*   `mapPartitions`는 가장 최적화된 방법이나, **코드 가독성**과 **안정성**을 고려해야 함.
    
*   데이터 규모가 클수록 `flatMap`, `mapPartitions`의 효과가 뚜렷함.
    
*   성능 최적화를 위해선, **연산 최소화**와 **함수 호출 줄이기**가 핵심이다.
    