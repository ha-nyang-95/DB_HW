# RDD

## RDD의 개념과 특징 이해

### RDD란?

### RDD의 특징

#### 1. 데이터의 추상화(Data Abstraction)

#### 2. 탄력성(Resilient) & 불변성(Immutable)

#### 3. Type-safe 기능

#### 4. 정형(Structured) & 비정형(Unstructured) 데이터

#### 5. 지연 평가(Lazy Evaluation)

### Spark RDD란?

#### 주요 구성 요소

- 의존성 정보
- 파티션(지역성 정보 포함)
- 연산 함수: Partition => Iterator[T]

## RDD 생성 및 변환 학습

### RDD 생성

#### 1. 기존의 메모리 데이터를 RDD로 변환하는 방법

#### 2. 외부파일(텍스트, CSV, JSON 등)에서 RDD를 생성하는 방법

#### Parallelize()

#### sc.textFile()

### RDD 변환

#### MAP

#### FLATMAP

#### FILTER

#### MAPPARTITIONS

#### KEYBY

#### JOIN

#### GROUPBY

#### GROUPBYKEY

#### Simulating GroupBy using GroupByKey

#### Word Counting Using GROUPBYKEY

#### Word Counting Using REDUCEBYKEY

#### REDUCEBYKEY vs GROUPBYKEY

#### GROUPBYKEY

#### REDUCEBYKEY

#### UNION

#### DISTINCT

#### COALESCE

#### PARTITIONBY

### RSS Fundamentals

#### Sample

#### COLLECT

#### COUNTBYKEY

#### REDUCE

#### SUM

#### MAX

#### MEAN

#### STDEV

### RDD Action

#### ACTIONS

#### RDD 데이터 불러오기와 저장하기
