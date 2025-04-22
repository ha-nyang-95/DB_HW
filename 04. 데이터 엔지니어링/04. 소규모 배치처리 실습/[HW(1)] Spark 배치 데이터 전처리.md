# Spark 배치 데이터 전처리


📘 1. 실습 주제 개요: 정해진 시간 단위로 데이터를 집계하는 윈도우 연산 실습
==============================================

💡 주제: PySpark로 구현하는 타임 윈도우 기반 배치 처리
------------------------------------

### 🎯 실습의 목적

현대의 데이터 분석 및 시스템 모니터링 환경에서는 실시간으로 유입되는 데이터를 **시간 단위로 집계**하는 요구가 많다. 예를 들어, "최근 10분 동안 발생한 로그 메시지의 개수", "5분마다 발생한 트랜잭션 수"와 같은 통계는 서비스 상태를 모니터링하거나 알림 시스템을 구현하는 데 핵심적인 지표가 된다.

이러한 요구를 충족하기 위해 Apache Spark는 **윈도우(Window) 함수**를 제공하며, 본 실습은 정해진 시간 단위로 데이터를 그룹화하고 집계하는 **시간 창 기반 집계**(Window Aggregation)를 수행하는 실습이다.

특히 이 실습은 배치 모드로 진행되지만, **스트리밍 환경과 유사한 윈도우 연산 처리 흐름**을 이해하는 데 초점을 둔다. 실시간 분석 시스템을 설계할 때의 개념적 기반을 제공하며, 이후 **Spark Structured Streaming** 혹은 **Flink**로 확장 가능하다.

### 🧠 배경 이론: 윈도우 연산이란?

윈도우 연산은 시간 단위로 데이터를 그룹화하는 기법으로, 다음과 같은 유형이 있다:

*   **Tumbling Window (고정 창)**: 겹치지 않고 연속된 시간 간격으로 데이터를 그룹화  
    예: 매 10분 단위로 집계
    
*   **Sliding Window (이동 창)**: 일정 간격으로 겹치며 시간 창을 적용  
    예: 10분 창을 5분 간격으로 슬라이딩
    
*   **Session Window (세션 창)**: 사용자 세션 또는 이벤트 흐름에 따라 동적으로 그룹화
    

본 실습은 **Tumbling Window**에 해당하며, 고정된 10분 단위로 `event_time` 필드 기준 데이터를 집계한다.

<br>
<br>

🛠️ 2. 코드 구조 및 흐름 해설 + 실행 결과 예시 및 해설
====================================

✅ 전체 흐름 요약
----------

이 코드는 다음과 같은 흐름을 따른다:

1.  **Spark 세션을 생성**한다.
    
2.  **CSV 파일을 로드**하면서 명시적으로 스키마를 정의한다.
    
3.  이벤트가 발생한 시간을 기준으로 **10분 단위 윈도우로 데이터를 그룹화**한다.
    
4.  각 윈도우 구간마다 메시지 개수를 **집계**한 후 정렬하여 출력한다.
    

<br>

🔍 코드 구조 및 해설
-------------

### 🔹 1) Spark 세션 생성

```python
spark = SparkSession.builder \
    .appName("CsvBatchProcessing") \
    .getOrCreate()
```

*   Spark는 분산 데이터 처리 프레임워크로, 모든 연산의 시작은 `SparkSession` 객체 생성부터 시작된다.
    
*   `appName`은 실행 중인 애플리케이션의 이름을 지정하며, Spark UI에서 확인 가능하다.
    

<br>

### 🔹 2) 데이터 스키마 정의

```python
schema = StructType() \
    .add("event_time", TimestampType()) \
    .add("message", StringType())
```

*   `StructType`은 데이터프레임의 스키마를 정의하는 역할을 한다.
    
*   이 실습에서는 `event_time`이 타임스탬프 형식임을 명시적으로 지정함으로써, Spark가 시간 연산을 정확하게 처리할 수 있도록 한다.
    
*   `message`는 분석 대상이 되는 로그 메시지 문자열이다.
    

<br>

### 🔹 3) CSV 파일 로드

```python
df = spark.read \
    .option("header", True) \
    .schema(schema) \
    .csv("../data/sample_events.csv")
```

*   `option("header", True)`는 CSV의 첫 줄을 컬럼명으로 인식하게 한다.
    
*   `.schema()`를 사용하면 자동 스키마 추론이 아닌 사용자 정의 스키마를 적용하여 정확도를 높일 수 있다.
    
*   파일 경로는 상대 경로로 지정되어 있으며, 실행 시 위치에 따라 조정 가능하다.
    

<br>

### 🔹 4) 시간 창 윈도우 그룹화 및 집계

```python
agg_df = df.groupBy(
    window(col("event_time"), "10 minutes")
).count()
```

*   핵심 로직이다. `window()` 함수는 `event_time`을 기준으로 **10분 간격으로 데이터를 그룹화**한다.
    
*   `groupBy(window(...)).count()`는 각 10분 구간마다 메시지 개수를 세는 작업이다.
    
*   반환된 `window`는 구조체(struct)로, 시작 시간(`start`)과 종료 시간(`end`) 정보를 포함한다.
    

<br>

### 🔹 5) 결과 출력

```python
agg_df.orderBy("window").show(truncate=False)
```

*   `.orderBy("window")`는 시간 순으로 윈도우를 정렬하여 출력한다.
    
*   `truncate=False`는 컬럼이 잘리지 않도록 설정하여 전체 출력을 보장한다.
    

<br>

📌 실행 결과 예시
-----------

실제 출력 예시는 다음과 유사하다:

```
+------------------------------------------+-----+
|window                                    |count|
+------------------------------------------+-----+
|{2024-01-01 00:00:00, 2024-01-01 00:10:00}|35   |
|{2024-01-01 00:10:00, 2024-01-01 00:20:00}|42   |
|{2024-01-01 00:20:00, 2024-01-01 00:30:00}|51   |
+------------------------------------------+-----+
```

*   첫 번째 열은 윈도우 구간이며, `{시작시간, 종료시간}` 형식이다.
    
*   두 번째 열은 해당 구간 내 메시지의 수를 의미한다.
    

<br>
<br>

⚙️ 3. 전체 코드 + 상세 주석
===================

```python
# PySpark의 핵심 객체를 불러옴
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, window
from pyspark.sql.types import StructType, StringType, TimestampType

# 1. Spark 세션 생성
# - 분산 처리를 위한 진입점 객체인 SparkSession 생성
spark = SparkSession.builder \
    .appName("CsvBatchProcessing") \  # 애플리케이션 이름 설정
    .getOrCreate()

# 2. 스키마 명시적 정의
# - CSV 파일을 로드할 때 컬럼의 데이터 타입을 정확히 지정하여 파싱 오류 방지
schema = StructType() \
    .add("event_time", TimestampType()) \  # 시간 정보 (예: 2024-04-21 15:30:00)
    .add("message", StringType())          # 메시지 내용 (예: "서비스 정상 작동 중")

# 3. CSV 파일 읽기
# - sample_events.csv 파일을 DataFrame으로 읽음
df = spark.read \
    .option("header", True) \  # 첫 줄을 컬럼명으로 처리
    .schema(schema) \          # 위에서 정의한 스키마 적용
    .csv("../data/sample_events.csv")  # 상대 경로로 파일 위치 지정

# 4. 시간 기준 윈도우 그룹화 및 메시지 개수 집계
# - 10분 단위로 event_time을 그룹화하고 각 구간의 메시지 수를 계산
agg_df = df.groupBy(
    window(col("event_time"), "10 minutes")  # 10분짜리 시간 창을 생성
).count()  # 각 윈도우 안에 포함된 레코드 수 계산

# 5. 결과 정렬 및 출력
# - 시간 순으로 윈도우를 정렬한 뒤 결과를 출력
agg_df.orderBy("window").show(truncate=False)
```

<br>

### 📝 주요 포인트 요약

| 요소 | 설명 |
| --- | --- |
| `SparkSession` | 모든 연산의 출발점, DataFrame 생성 및 연산 수행 |
| `StructType` | 컬럼의 데이터 타입을 명시하여 정확한 파싱 가능 |
| `window()` | 시간 기반 집계를 가능하게 하는 핵심 함수 |
| `groupBy().count()` | 윈도우 단위로 메시지 개수 집계 |
| `orderBy("window")` | 시간 순으로 결과 정렬 |

<br>
<br>

📚 4. 추가 설명 및 실무 팁
==================

❗ 자주 발생하는 실수와 주의사항
------------------

### ① Timestamp 타입 파싱 실패

*   **문제**: `event_time` 컬럼이 `"2024-04-21 12:30:00"`과 같은 문자열로 되어 있음에도 `StringType()`으로 잘못 지정하거나, 스키마를 생략하면 시간 연산이 불가능함.
    
*   **해결**: 반드시 `TimestampType()`으로 명시하거나, `to_timestamp()` 함수로 명시적 변환 필요.
    

```python
from pyspark.sql.functions import to_timestamp
df = df.withColumn("event_time", to_timestamp("event_time"))
```

<br>

### ② 윈도우 기준 컬럼 누락

*   `window()` 함수는 반드시 시간 타입 컬럼에 적용해야 함. `StringType`이나 `IntegerType` 컬럼에 적용할 경우 오류 발생.
    

<br>

### ③ 시간대(Timezone) 이슈

*   데이터가 UTC 기준일 경우, 결과가 한국 시간과 맞지 않는 경우가 있음.
    
*   `spark.conf.set("spark.sql.session.timeZone", "Asia/Seoul")` 명령으로 세션 시간대를 맞출 수 있음.
    

<br>

💼 실무에서의 활용 예시
--------------

| 산업 | 활용 사례 |
| --- | --- |
| 모니터링 시스템 | 1분 단위 서버 장애 로그 집계 |
| 금융 거래 분석 | 5분 단위 주식 매매량 추이 분석 |
| IoT 센서 데이터 | 10초 간격의 온도/습도 데이터 집계 |
| 사용자 행동 분석 | 30분 간격 웹사이트 방문 수 집계 |

*   실시간 분석이 필요한 거의 모든 산업에서 **윈도우 기반 집계**는 핵심 기술로 활용됨.
    
*   특히 Spark Streaming이나 Flink에서 이 개념은 **스트리밍 상태 관리의 기초**로 이어짐.
    

<br>

🌱 확장 방향 및 심화 학습
----------------

### 🔹 Structured Streaming 으로 확장

*   동일한 코드를 Spark Structured Streaming으로 확장하면, 실시간 데이터 처리 가능.
    
*   입력 소스를 Kafka, 소켓, 파일 등으로 교체 가능.
    

### 🔹 다양한 윈도우 유형 실습

*   **슬라이딩 윈도우** (`window(col("ts"), "10 minutes", "5 minutes")`)
    
*   **세션 윈도우** (`session_window(...)`) 도입 시 사용자 중심 이벤트 분석 가능
    

<br>

🧠 마무리 요약
---------

본 실습은 단순한 배치 처리처럼 보이지만, 실제로는 **스트리밍 데이터 처리에 필요한 시간 집계의 개념을 내포**하고 있다. 정해진 시간 간격으로 데이터를 나누고 요약하는 과정은, 대규모 데이터 속에서 패턴을 읽고 이상을 탐지하며 시스템을 이해하는 데 중요한 기반을 제공한다.

시간 기반 데이터 분석은 단순히 "언제 일어났는가"를 넘어서, **"주기적 패턴 속에서 무슨 일이 발생하고 있는가"를 탐색하는 기술**이며, 본 실습은 그 시작점이 된다.
