📘 RDD 샘플링 및 분할 실습 정리본
======================

✨ 실습 목표
-------

*   PySpark의 `RDD`를 활용하여 데이터를 생성하고,
    
*   `sample()`, `takeSample()`을 통해 **샘플링**을 수행하며,
    
*   `randomSplit()`을 이용한 **데이터 분할**을 실습해본다.
    
*   각각의 샘플링 방식 및 분할 결과를 비교 분석한다.
    

* * *

📌 1. SparkContext 생성
---------------------

```python
from pyspark import SparkContext
sc = SparkContext("local", "SamplingSplitApp")
```

*   `SparkContext`: Spark의 **핵심 진입점**으로, 클러스터와의 연결을 설정하고 작업을 수행하는 데 사용됨.
    
*   `"local"`: 현재 로컬 머신에서 실행할 것을 지정.
    
*   `"SamplingSplitApp"`: 애플리케이션 이름 (로그나 웹 UI에서 식별용).
    

* * *

📌 2. RDD 생성
------------

```python
numbers_rdd = sc.parallelize(range(1, 101))
```

*   `sc.parallelize()`: 리스트나 범위를 **RDD로 변환**.
    
*   여기서는 1~100까지 숫자를 RDD로 만들어서 **100개의 데이터를 가진 RDD**를 생성함.
    
*   `.count()`: RDD의 총 개수를 반환.
    

```python
print(f"원본 데이터 개수: {numbers_rdd.count()}")
# 출력: 원본 데이터 개수: 100
```

* * *

📌 3. sample(): RDD 샘플링
-----------------------

### ① 비복원 샘플링

```python
sample_without = numbers_rdd.sample(False, 0.2)
```

*   `sample(withReplacement, fraction)`
    
*   `withReplacement=False`: 비복원 샘플링 (같은 값은 한 번만 선택됨).
    
*   `fraction=0.2`: 전체 데이터의 약 20%를 샘플로 추출.
    

```python
print("비복원 샘플링 결과:", sample_without.collect())
# 예시 출력: [4, 16, 23, 27, ...] (결과는 실행마다 달라짐)
```

### ② 복원 샘플링

```python
sample_with = numbers_rdd.sample(True, 0.2)
```

*   `withReplacement=True`: 복원 샘플링 (같은 값이 여러 번 나올 수 있음).
    
*   `0.2`: 각 항목이 선택될 **확률**이므로, 데이터 수의 20%가 샘플로 나온다고 보장할 수 없음.
    

```python
print("복원 샘플링 결과:", sample_with.collect())
# 예시 출력: [5, 15, 16, 25, 50, 50, ...]
```

* * *

📌 4. takeSample(): 개수 기반 샘플링
-----------------------------

### ① 비복원 방식

```python
take_sample_without = numbers_rdd.takeSample(False, 5)
```

*   `takeSample(withReplacement, num)`: `num`개만큼 샘플을 추출.
    
*   비복원 → 중복 없이 5개 선택.
    

```python
print("takeSample 비복원:", take_sample_without)
# 예시: [3, 64, 54, 77, 95]
```

### ② 복원 방식

```python
take_sample_with = numbers_rdd.takeSample(True, 5)
```

*   복원 → 중복 허용됨.
    

```python
print("takeSample 복원:", take_sample_with)
# 예시: [18, 13, 30, 23, 85]
```

* * *

📌 5. randomSplit(): 훈련/테스트 데이터 분할
----------------------------------

```python
train_rdd, test_rdd = numbers_rdd.randomSplit([0.8, 0.2], seed=42)
```

*   `randomSplit(weights, seed)`: 비율 기반으로 RDD 분할.
    
*   `[0.8, 0.2]`: 전체 데이터를 8:2로 분할.
    
*   `seed`: 랜덤 시드를 고정하여 동일 결과 재현 가능.
    

```python
print(f"훈련 데이터 개수: {train_rdd.count()}")
print(f"테스트 데이터 개수: {test_rdd.count()}")
```

※ 분할 시 정확히 80개/20개가 아닌 약간의 차이는 있을 수 있음 (확률 기반 분할).

* * *

📌 6. 샘플 개수 비교 분석
-----------------

```python
print(f"비복원 샘플 개수: {sample_without.count()}")
print(f"복원 샘플 개수: {sample_with.count()}")
```

*   `.count()`를 통해 샘플링된 RDD의 실제 데이터 개수를 비교.
    
*   복원 샘플은 중복 허용이므로 더 많아질 수 있음.
    

* * *

📌 7. 전체 코드
-----------------

```python
from pyspark import SparkContext
sc = SparkContext("local", "SamplingSplitApp")

# 1. 1~100까지 숫자 데이터를 RDD로 생성
# 원본 데이터 개수: 100
numbers_rdd = sc.parallelize(range(1, 101))
print(f"원본 데이터 개수: {numbers_rdd.count()}")

# 2. sample() 비복원 방식으로 20% 샘플링
# 비복원 샘플링 결과: [4, 16, 23, 27, 28, 36, 40, 42, 57, 63, 67, 74, 78, 81, 86]
sample_without = numbers_rdd.sample(False, 0.2)
print("비복원 샘플링 결과:", sample_without.collect())

# sample() 복원 방식으로 20% 샘플링
# 복원 샘플링 결과: [5, 15, 16, 25, 29, 33, 38, 41, 48, 50, 50, 54, 56, 65, 81, 83, 89, 92, 93]
sample_with = numbers_rdd.sample(True, 0.2)
print("복원 샘플링 결과:", sample_with.collect())

# takeSample() 비복원
# takeSample 비복원: [3, 64, 54, 77, 95]
take_sample_without = numbers_rdd.takeSample(False, 5)
print("takeSample 비복원:", take_sample_without)

# takeSample() 복원
# takeSample 복원: [18, 13, 30, 23, 85]
take_sample_with = numbers_rdd.takeSample(True, 5)
print("takeSample 복원:", take_sample_with)

# 3. randomSplit()으로 훈련/테스트 분할
# 훈련 데이터 개수: 81
# 테스트 데이터 개수: 19
train_rdd, test_rdd = numbers_rdd.randomSplit([0.8, 0.2], seed=42)
print(f"훈련 데이터 개수: {train_rdd.count()}")
print(f"테스트 데이터 개수: {test_rdd.count()}")

# 4. 비교 분석
# 비복원 샘플 개수: 15
# 복원 샘플 개수: 19
print(f"비복원 샘플 개수: {sample_without.count()}")
print(f"복원 샘플 개수: {sample_with.count()}")
```

* * *

📊 결과 요약 표
----------

| 구분            | 방식        | 함수                      | 중복 | 개수 보장 | 예시 출력              |
| --------------- | ----------- | ------------------------- | ---- | --------- | ---------------------- |
| `sample()`      | 비복원      | `sample(False, 0.2)`      | ❌    | ❌         | \[4, 16, ...\]         |
| `sample()`      | 복원        | `sample(True, 0.2)`       | ✅    | ❌         | \[5, 15, 50, 50, ...\] |
| `takeSample()`  | 비복원      | `takeSample(False, 5)`    | ❌    | ✅         | \[3, 54, 95, ...\]     |
| `takeSample()`  | 복원        | `takeSample(True, 5)`     | ✅    | ✅         | \[30, 30, 85, ...\]    |
| `randomSplit()` | 데이터 분할 | `randomSplit([0.8, 0.2])` | \-   | 비율기반  | 훈련/테스트 분할       |

* * *

🧠 핵심 개념 요약
-----------

| 용어               | 설명                                                      |
| ------------------ | --------------------------------------------------------- |
| RDD                | 분산된 데이터 집합으로 Spark의 핵심 데이터 구조           |
| 샘플링             | 전체 데이터 중 일부만 선택하여 대표로 사용하는 기법       |
| 복원/비복원 샘플링 | 선택된 데이터를 다시 뽑을 수 있는지 여부 (중복 허용 여부) |
| `sample()`         | 비율 기반 샘플링                                          |
| `takeSample()`     | 개수 기반 샘플링                                          |
| `randomSplit()`    | 비율 기반 RDD 분할                                        |
| `collect()`        | RDD를 리스트로 변환 (로컬로 가져오기)                     |
| `count()`          | RDD의 총 데이터 개수 반환                                 |

* * *

📌 실습을 통해 얻은 인사이트
-----------------

*   RDD의 `sample()`과 `takeSample()`은 목적에 따라 다르게 사용해야 한다.
    
*   학습용 데이터셋을 만들 때는 `randomSplit()`이 유용하다.
    
*   복원 샘플링은 데이터 중복이 허용되므로 주의해서 사용해야 한다.
    
*   실시간으로 결과가 달라질 수 있으므로, 동일 실험을 재현하려면 `seed` 설정이 중요하다.
