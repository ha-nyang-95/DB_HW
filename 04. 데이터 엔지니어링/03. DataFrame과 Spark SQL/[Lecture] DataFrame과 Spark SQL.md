# 📘 DataFrame과 Spark SQL
```text
[Abstract]
Apache Spark의 핵심 구성 요소인 DataFrame과 Spark SQL에 대한 포괄적인 학습 내용을 정리한 것으로,
특히 컴퓨터공학 비전공자도 Spark의 구조화된 데이터 처리 방식을 실습 중심으로 이해할 수 있도록 구성되었다.

기존의 RDD(Resilient Distributed Dataset)는 Spark의 분산 처리 기반을 제공했지만,
스키마 정보의 부재와 복잡한 함수 기반 API로 인해 실무에서 활용하기에 불편함이 많았다.

이에 본 자료는 이러한 한계를 극복한 DataFrame과 Spark SQL의 구조적 장점과 실용성을 중심으로 설명하며,
스키마 기반의 구조화, SQL과의 통합, Catalyst 엔진에 의한 자동 최적화 등의 기능을 실제 예제와 함께 소개한다.

문서 구성은 개념적 비교(RDD vs DataFrame vs Dataset)를 시작으로,
DSL(Python 기반 API)과 SQL 쿼리를 활용한 데이터 생성, 조회, 조건 처리, 집계, 정렬, 문자열 처리, 결측값 처리 등의
핵심 기능을 양식별(DSL/SQL) 로 나누어 직관적으로 학습할 수 있도록 구성하였다.
```

<br>

## 1. DataFrame과 Spark SQL의 개념과 활용법 이해
***
### 1.1 SparkSQL, DataFrame, Dataset의 개념
***
**- RDD API의 문제점**         


Spark는 원래 RDD (Resilient Distributed Dataset) 를 기반으로 데이터를 처리하는 구조를 가지고 있습니다.  
RDD는 분산 처리에 있어 강력한 기능을 제공하지만, 실무 환경에서 활용하기에는 몇 가지 불편한 점이 존재합니다. 
이에 따라 아래와 같이 RDD의 주요 한계점을 정리하였습니다:


✅ 1. 복잡한 코드   
RDD는 DataFrame이나 SQL처럼 "컬럼 이름"이 없어도 사용할 수 있다는 장점이 있지만,
모든 데이터를 map, filter, reduce 등의 저수준 함수로 처리해야 하기 때문에
전체 코드가 길고 복잡해질 수 있다는 단점이 존재합니다.

```python
# RDD를 사용한 예시
rdd = sc.textFile("data.csv")
header = rdd.first()
data = rdd.filter(lambda row: row != header)
columns = data.map(lambda row: row.split(","))
```     

✅ 2. 성능 최적화의 어려움
RDD는 내부적으로 어떤 연산을 어떻게 최적화할지 Spark가 자동으로 판단하기 어려운 구조입니다.     
따라서 사용자가 직접 최적화 로직을 고려해야 하며,
이는 전체적인 성능 저하로 이어질 수 있는 요인이 됩니다.     

✅ 3. 스키마(컬럼 이름, 타입) 정보의 부재   
RDD는 단순한 "데이터 집합"으로써, 컬럼 이름이나 데이터 타입 등 구조화된 정보가 존재하지 않습니다.   
이로 인해 데이터 분석이나 전처리 과정에서 직관적인 작업이 어렵고, 유지 보수도 불편합니다.

✅ 4. SQL 문법 사용의 제약  
RDD는 SQL에서 자주 사용하는 SELECT, WHERE, GROUP BY 등의 문법을 직접 사용할 수 없습니다.    
따라서 SQL에 익숙한 사용자 입장에서는 데이터 조작의 진입 장벽이 높아지는 단점이 있습니다.


🔎 이러한 문제를 해결하기 위해 등장한 것이?         
- 바로 DataFrame과 Spark SQL입니다.

<br>

**- Spark SQL과 DataFrame 소개**  


RDD의 단점을 보완하기 위해 **DataFrame**과 **Spark SQL**이 도입되었습니다.  
특히 비전공자 입장에서는 "엑셀 표와 유사한 형태의 데이터"라고 이해하면 DataFrame의 개념을 보다 쉽게 받아들일 수 있습니다.

<br>

  - DataFrame이란?   
    DataFrame은 **컬럼 이름과 데이터 타입(스키마)** 을 갖는 **2차원 테이블 형태의 데이터 구조**입니다.   
    Pandas의 DataFrame과 명칭은 동일하지만, **Spark의 DataFrame은 분산 처리를 지원한다는 점**에서 차별화됩니다.              
    
    📋 예를 들면 다음과 같은 구조입니다:    
    | name | age | city |
    | ---- | --- | ---- |
    | 철수 | 25  | 서울 |
    | 영희 | 30  | 부산 |
    | 민수 | 28  | 대전 |

    이와 같은 표 형태의 데이터를 DataFrame으로 표현할 수 있으며, 각 열은 하나의 컬럼으로 구성됩니다.  
    
    <br>

    ✅ DataFrame의 장점     
    | 장점                        | 설명                                                   |
    | --------------------------- | ------------------------------------------------------ |
    | 스키마 보유                 | 컬럼 이름, 데이터 타입이 명확해서 가독성과 분석이 쉬움 |
    | SQL 사용 가능               | SQL 쿼리로 데이터 조작 가능 (ex. SELECT \* FROM ...)   |
    | 최적화 가능 (Catalyst 엔진) | Spark 내부 엔진이 쿼리를 자동으로 최적화해줘           |
    | 통합 API 제공               | Python, Java, Scala 등 여러 언어에서 동일한 API 제공   |

    <br>

    💬 DataFrame은 어떻게 다루냐면?
    ```python
    # 예제
    from pyspark.sql import SparkSession

    spark = SparkSession.builder.appName("DataFrameExample").getOrCreate()

    data = [("철수", 25, "서울"), ("영희", 30, "부산")]
    columns = ["name", "age", "city"]

    df = spark.createDataFrame(data, columns)
    df.show()
    ```
    출력
    ```pqsql
    +-----+---+------+
    | name|age|  city|
    +-----+---+------+
    | 철수| 25|  서울|
    | 영희| 30|  부산|
    +-----+---+------+
    ``` 
    
    <br>
    
    🔧 Spark SQL이란?
    Spark SQL은 **SQL 쿼리를 활용해 DataFrame을 조작할 수 있도록 해주는 기능**입니다.
    즉, DataFrame을 데이터베이스의 테이블처럼 활용하여 `SELECT`, `WHERE`, `GROUP BY` 등의 문법을 사용할 수 있습니다.
    ```python
    df.createOrReplaceTempView("people")
    spark.sql("SELECT * FROM people WHERE age > 25").show()
    ```     

    <br>

    🔄 관계 정리
    | 요소          | 특징                                                  |
    | ------------- | ----------------------------------------------------- |
    | **RDD**       | 낮은 수준의 API, 구조 없음, 연산은 많지만 사용 어려움 |
    | **DataFrame** | 구조화된 데이터 (컬럼, 타입), 고성능 처리 가능        |
    | **Spark SQL** | DataFrame을 SQL처럼 처리할 수 있게 해주는 언어 도구   |
    
<br>

  - DataFrame API 개요  
    DataFrame은 단순한 표 형태의 구조를 가질 뿐만 아니라,  
    **다양한 메서드(API)** 를 통해 **데이터를 가공하고 분석할 수 있는 기능**을 함께 제공합니다.      
    
    🔧 주요 기능 예시 (코드는 Python 기준)

    | 기능            | 설명             | 예시                                    |
    | --------------- | ---------------- | --------------------------------------- |
    | `.show()`       | 데이터 조회      | `df.show()`                             |
    | `.select()`     | 컬럼 선택        | `df.select("name", "age")`              |
    | `.filter()`     | 조건 필터링      | `df.filter(df.age > 25)`                |
    | `.groupBy()`    | 그룹화 및 집계   | `df.groupBy("city").count()`            |
    | `.withColumn()` | 새로운 컬럼 추가 | `df.withColumn("age_plus", df.age + 1)` |
    | `.drop()`       | 컬럼 제거        | `df.drop("city")`                       |
    | `.orderBy()`    | 정렬             | `df.orderBy("age", ascending=False)`    |

    이러한 API는 SQL에서 수행하던 작업과 거의 동일한 기능을 제공하며,  
    다만 차이점은 **SQL 문법이 아닌 프로그래밍 코드 형태로 작성한다는 점**입니다.   

<br>

  - DataFrame API - 데이터 타입         
    DataFrame의 각 컬럼은 **명확한 데이터 타입**을 가지고 있으며,       
    이를 이해하고 활용함으로써 **타입 오류를 방지하고 안정적인 데이터 처리**가 가능합니다.      

    🎯 주요 데이터 타입

    | Spark 타입      | 설명                      | Python 타입과 비교 |
    | --------------- | ------------------------- | ------------------ |
    | `StringType`    | 문자열 데이터             | `str`              |
    | `IntegerType`   | 정수형 데이터             | `int`              |
    | `DoubleType`    | 실수형 데이터             | `float`            |
    | `BooleanType`   | 논리형 (참/거짓)          | `bool`             |
    | `TimestampType` | 날짜 및 시간 데이터       | `datetime`         |
    | `ArrayType`     | 배열 형태 데이터          | `list`             |
    | `StructType`    | 중첩 구조 (Nested Struct) | `dict` 또는 객체   |

    예시: 스키마 정의 및 타입 확인

    ```python
    df.printSchema()
    ```

    출력 예시:

    ```
    root
    |-- name: string (nullable = true)
    |-- age: long (nullable = true)
    |-- city: string (nullable = true)
    ```

    위 예시에서 `name`, `city`는 `string`, `age`는 `long` (정수형)에 해당합니다.

<br>

  - DataFrame API - 스키마(Schema)              
    **스키마(Schema)** 란 DataFrame의 **컬럼 구조 및 데이터 타입 정보를 명확히 정의한 설계도**입니다.               
    스키마 정보를 명시함으로써 데이터에 대한 명확한 구조를 사전에 설정할 수 있으며,         
    이는 오류 방지 및 코드 가독성 측면에서 매우 유리합니다.    

    | 요소          | 의미                                              |
    | ------------- | ------------------------------------------------- |
    | 컬럼 이름     | 각 열의 고유 명칭 (예: name, age)                 |
    | 데이터 타입   | 각 컬럼의 자료형 (예: StringType, IntegerType 등) |
    | Nullable 여부 | null 값 허용 여부 (True 또는 False)               |

    <br>    

    📄 스키마 수동 지정 예시

    ```python
    from pyspark.sql.types import StructType, StructField, StringType, IntegerType

    schema = StructType([
        StructField("name", StringType(), True),
        StructField("age", IntegerType(), True)
    ])

    df = spark.createDataFrame([("철수", 25), ("영희", 30)], schema)
    df.printSchema()
    ```

    위 코드에서 `StructType`은 테이블 전체의 구조를 정의하고,  
    `StructField`는 각 개별 컬럼의 타입과 null 허용 여부를 정의하는 역할을 합니다.

<br>

  - DataFrame 구성 요소         
    DataFrame은 겉보기에는 엑셀과 유사한 **표(table)** 형태로 표현되지만,           
    내부적으로는 **RDD 위에 스키마 정보를 덧붙인 구조**로 구성되어 있습니다.        

    이 구조는 다음과 같은 계층으로 이해할 수 있습니다:      
    ```
    ┌────────────┐
    │  DataFrame │  ← 사용자 입장에서 보이는 표 형식의 데이터
    └─────┬──────┘
        ↓
    ┌────────────┐
    │    RDD     │  ← 실질적인 분산 데이터 저장소
    └─────┬──────┘
        ↓
    ┌────────────────────┐
    │  Row 객체 + Schema │  ← 컬럼명, 데이터 타입 등의 구조 정보 포함
    └────────────────────┘
    ```

    즉, DataFrame은 RDD를 기반으로 하되, 여기에 **컬럼명과 데이터 타입을 포함한 스키마 정보를 추가하여**  
    보다 구조적이고 직관적인 데이터 처리가 가능하도록 구성된 것입니다.

<br>

**- RDD와 DataFrame의 차이점**


| 항목               | RDD                          | DataFrame                        |
| ------------------ | ---------------------------- | -------------------------------- |
| 구조 정보          | 없음                         | 있음 (스키마 기반)               |
| 사용 편의성        | 낮음 (저수준 API)            | 높음 (고수준 API)                |
| 성능 최적화        | 어려움                       | Catalyst 엔진에 의한 자동 최적화 |
| SQL 사용 가능 여부 | 불가능                       | 가능 (Spark SQL 연동)            |
| 타입 안정성        | 낮음 (런타임 오류 발생 가능) | 높음 (정적 스키마 기반)          |

<br>

🔍 실제로 사용해보면 어떤 차이가 있을까?

```python
# RDD 방식 (구조화되지 않은 처리 방식)
rdd = sc.parallelize([("철수", 25), ("영희", 30)])
rdd.map(lambda x: (x[0], x[1] + 1)).collect()

# DataFrame 방식 (구조화된 데이터, 직관적인 처리 방식)
df = spark.createDataFrame([("철수", 25), ("영희", 30)], ["name", "age"])
df.withColumn("age_plus", df.age + 1).show()
```

위 예시처럼, DataFrame은 **컬럼명 기반의 가공이 가능하고 가독성도 우수**하여  
복잡한 작업도 상대적으로 간단하게 처리할 수 있습니다.

    
<br>

**- RDD를 사용하는 경우**   


DataFrame이 일반적으로 더 직관적이고 성능도 우수하지만,         
**특수한 상황이나 복잡한 처리 로직이 필요한 경우에는 여전히 RDD의 활용이 유효**합니다.

**✅ 다음과 같은 상황에서는 RDD를 사용하는 것이 적합합니다:**

1.  **복잡한 데이터 변환이 필요한 경우**
    
    *   예: 중첩된 반복문이나 사용자 정의 로직이 포함된 복잡한 처리 과정
        
2.  **데이터 구조가 유동적인 경우**
    
    *   예: JSON 파일처럼 각 행마다 컬럼 구조가 다를 수 있는 비정형 데이터
        
3.  **저수준 제어가 필요한 경우**
    
    *   예: 캐시 전략, 파티셔닝, MapReduce 스타일의 세밀한 제어가 필요한 경우
        
4.  **기존에 RDD 기반으로 개발된 시스템을 유지/확장하는 경우**
    

<br>

정리하자면,

> ✅ **일반적인 데이터 분석과 처리에는 DataFrame을 사용하는 것이 권장**되며,  
> 🔧 **특수한 제약 조건이나 고난이도 처리가 필요한 경우에 한해 RDD 사용을 고려**하면 됩니다.

<br>

### 1.2 SparkSQL의 이해

***

**- SparkSQL이란?**    


> SparkSQL은 **SQL 쿼리 언어를 이용하여 분산 데이터를 처리할 수 있도록 지원하는 Spark의 핵심 구성 요소**입니다.  
> 사용자는 SQL 문법(`SELECT`, `WHERE`, `GROUP BY` 등)을 통해 **DataFrame을 데이터베이스처럼 조작**할 수 있습니다.

**✔️ SparkSQL의 핵심 개념**

*   SQL 쿼리를 사용할 수 있게 해주는 **언어 수준의 인터페이스**
    
*   **DataFrame 및 Dataset에 SQL 문법을 직접 적용**할 수 있도록 지원
    
*   내부적으로는 SQL 쿼리를 분석하고 **최적화 과정을 거쳐 실행 계획을 생성**함

<br>

**- SparkSQL의 역할**           


| 역할                    | 설명                                                                        |
| ----------------------- | --------------------------------------------------------------------------- |
| SQL 인터페이스 제공     | SQL 문법을 통해 DataFrame을 조회하고 가공할 수 있음                         |
| 뷰(View) 생성           | DataFrame을 SQL 테이블처럼 등록하여 사용 가능                               |
| 쿼리 최적화             | Catalyst Optimizer를 통해 쿼리를 자동으로 최적화                            |
| 다양한 데이터 소스 통합 | Hive, JSON, Parquet, JDBC 등 여러 포맷의 데이터 소스를 SQL로 통합 처리 가능 |

**📌 예시**

```python
df = spark.read.csv("people.csv", header=True, inferSchema=True)
df.createOrReplaceTempView("people")

# SQL 쿼리 실행
result = spark.sql("SELECT name, age FROM people WHERE age >= 25")
result.show()
```

<br>

**- SparkSQL의 내부 작동 방식**   


SQL 쿼리는 다음과 같은 다섯 단계의 과정을 거쳐 실행됩니다:

```
1. SQL 파싱 (Parsing)
   - 사용자가 입력한 SQL 쿼리를 트리 구조로 변환 (문법 분석)

2. 논리 계획 생성 (Logical Plan)
   - SQL의 의미를 논리적으로 표현 (예: Select → Filter → Project)

3. 최적화 (Optimization)
   - Catalyst 엔진이 불필요한 연산을 제거하거나 순서를 조정하여 실행 계획 최적화

4. 물리 계획 생성 (Physical Plan)
   - 실제 클러스터에서 실행 가능한 명령 형태로 변환

5. 실행 (Execution)
   - 최종 실행 계획이 클러스터에 분산되어 병렬로 처리됨
```

> Catalyst Optimizer는 Spark SQL의 핵심 엔진으로,  
> 사용자가 작성한 SQL 쿼리를 **더 효율적인 방식으로 자동 변환**하여 실행합니다.

<br>

**- SparkSQL과 DataFrame API의 관계**   


SparkSQL과 DataFrame은 **완전히 별개의 기술이 아니라, 내부적으로 동일한 실행 엔진을 공유**합니다.     
즉, SQL 문법이든 DataFrame 메서드든 **결국 동일한 Catalyst 엔진이 이를 처리**합니다.
    
| SQL 문법                  | DataFrame API            |
| ------------------------- | ------------------------ |
| `SELECT name FROM people` | `df.select("name")`      |
| `WHERE age > 30`          | `df.filter(df.age > 30)` |
| `ORDER BY age`            | `df.orderBy("age")`      |

결론적으로,

> 사용자는 **SQL 방식과 DSL 방식 중 편한 방식을 선택해 작업할 수 있으며**,  
> 내부적으로는 동일한 최적화 및 실행 구조에 의해 처리됩니다.

<br>

### 1.3 SparkSQL vs DataFrame vs Dataset

***

**- SparkSQL, DataFrame, Dataset 비교**  


Spark에서는 데이터를 처리하기 위한 **세 가지 주요 방식**을 제공합니다.          
각 방식은 서로 다른 인터페이스와 장단점을 가지며, 아래와 같이 비교할 수 있습니다.       


| 항목        | Spark SQL                       | DataFrame                    | Dataset _(Scala/Java only)_           |
| ----------- | ------------------------------- | ---------------------------- | ------------------------------------- |
| 인터페이스  | SQL 문자열                      | DataFrame API                | Dataset API                           |
| 언어 지원   | SQL 문법                        | Python, Scala, Java, R 등    | Scala, Java 전용                      |
| 타입 안정성 | 낮음 (런타임 오류 발생 가능)    | 낮음 (런타임 오류 발생 가능) | 높음 (컴파일 타임에서 타입 검증 가능) |
| 사용 난이도 | 낮음 (SQL 문법에 익숙하면 쉬움) | 중간 (프로그래밍 기반 조작)  | 높음 (정적 타입 명시 필요)            |
| 성능        | Catalyst 엔진에 의한 최적화     | Catalyst 엔진에 의한 최적화  | Catalyst + Tungsten 최적화            |


**📌 간단하게 요약하면?**

*   **Spark SQL**  
    → SQL 문법에 익숙한 사용자에게 적합한 방식입니다.  
    → 직관적이지만 **컴파일 타임에서의 타입 오류 검증은 제공되지 않습니다**.
    
*   **DataFrame**  
    → 프로그래밍 코드 기반의 고수준 API로, SQL보다 유연한 로직 구성이 가능합니다.  
    → 하지만 여전히 **동적 타입 기반이므로, 타입 안정성은 낮은 편입니다**.
    
*   **Dataset** _(Scala/Java 전용)_  
    → DataFrame과 RDD의 장점을 결합한 방식으로,  
    **정적 타입 시스템과 강력한 성능 최적화**를 동시에 제공합니다.  
    → 단, **Python에서는 사용이 불가능**하며, Scala 또는 Java 환경에서만 활용됩니다.
    
<br>

> ✅ 따라서 일반적으로는 **Python 환경에서는 DataFrame과 Spark SQL을 조합하여 사용하는 것이 가장 실용적이며**,  
> 정적 타입과 성능 모두를 고려해야 하는 경우에는 Scala 기반의 Dataset을 선택할 수 있습니다.

<br>

**- Dataset API 개요**   


앞서 언급했듯이, Dataset은 Python에서는 제공되지 않지만             
**Scala/Java 환경에서는 타입 안정성과 성능 최적화 측면에서 매우 강력한 선택지**가 될 수 있습니다.           

```scala
// Scala 예시
case class Person(name: String, age: Int)
val ds = Seq(Person("철수", 25), Person("영희", 30)).toDS()
ds.filter(_.age > 25).show()
```

위 예시처럼 `Person` 클래스와 같은 사용자 정의 타입을 기반으로 Dataset을 구성하면,  
**컴파일 타임에 타입 오류를 사전에 방지**할 수 있으며,  
람다식 기반 연산을 통해 **유지보수성과 실행 효율성 모두를 확보**할 수 있습니다.

<br>

**- View 등록 및 SQL 실행**         
Spark에서는 DataFrame을 SQL 테이블처럼 다룰 수 있도록,  
**임시 뷰(View)를 생성**하여 SQL 쿼리를 실행할 수 있습니다.

```python
df.createOrReplaceTempView("people")
spark.sql("SELECT * FROM people WHERE age > 25").show()
```

*   `createOrReplaceTempView("이름")` → SQL에서 사용할 임시 뷰로 등록
    
*   `spark.sql("...")` → SQL 쿼리 실행
    

💡 이러한 방식을 활용하면, **DataFrame과 SQL 간의 자유로운 전환 및 혼용**이 가능합니다.


<br>

**- DataFrame 구조 변환**    


DataFrame을 사용하다 보면, **컬럼 추가, 이름 변경, 컬럼 삭제, 스키마 재정의**와 같은 작업이 자주 발생합니다.  
아래는 그에 대한 대표적인 예시입니다:

**예시 1: 컬럼 추가**

```python
df.withColumn("age_plus_5", df.age + 5)
```

**예시 2: 컬럼 이름 변경**

```python
df.withColumnRenamed("age", "user_age")
```

**예시 3: 컬럼 삭제**

```python
df.drop("city")
```

**예시 4: 스키마 변경 (수동 정의)**

```python
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

schema = StructType([
    StructField("name", StringType(), True),
    StructField("age", IntegerType(), True)
])

df2 = spark.createDataFrame([("지민", 28)], schema)
df2.printSchema()
```

정리하면,

> SparkSQL은 SQL 문법에 친숙한 사용자에게 적합한 방식이며,  
> DataFrame은 Python 환경에서 구조화된 데이터를 유연하게 처리할 수 있는 고수준 API입니다.  
> Dataset은 정적 타입 기반의 컴파일 안정성과 성능을 모두 갖춘 고급 방식으로,  
> **Scala 및 Java 환경에서의 고성능 분석 작업에 적합합니다.**

<br>

## 2. SQL을 활용한 데이터 처리 학습

***

### 2.1 Spark SQL 기본 문법 및 데이터프레임 생성

***

**- SQL 쿼리 기본 문법**   

Spark SQL은 **일반적인 관계형 데이터베이스(SQL)** 와 매우 유사한 문법을 따릅니다.  
따라서 SQL에 익숙한 사용자라면 어렵지 않게 사용할 수 있으며,  
아래는 자주 사용되는 기본 문법을 정리한 표입니다:

| 구문        | 설명             | 예시                                       |
| ----------- | ---------------- | ------------------------------------------ |
| `SELECT`    | 컬럼 선택        | `SELECT name, age FROM people`             |
| `WHERE`     | 조건 필터링      | `WHERE age > 30`                           |
| `GROUP BY`  | 그룹별 집계      | `GROUP BY city`                            |
| `ORDER BY`  | 정렬             | `ORDER BY age DESC`                        |
| `LIMIT`     | 결과 제한        | `LIMIT 10`                                 |
| `AS`        | 컬럼에 별칭 부여 | `SELECT age AS user_age`                   |
| `CASE WHEN` | 조건 분기 처리   | `CASE WHEN age > 30 THEN 'O' ELSE 'X' END` |

→ SQL 문법을 익힌 사용자라면 매우 직관적으로 사용할 수 있습니다.

<br>

**- DataFrame 생성 방법**   

Spark에서 DataFrame을 생성하는 방법은 다음과 같이 **크게 세 가지 방식**으로 나뉩니다.

1.  **DSL 코드 기반 생성** (프로그래밍 코드로 직접 정의)
    
2.  **SQL 코드 기반 생성** (임시 뷰를 활용한 SQL 쿼리 방식)
    
3.  **외부 파일 불러오기 방식** (CSV, JSON 등)

    1️⃣ Creating DataFrames – DSL 코드 
 
    DSL 방식은 **프로그래밍 코드로 직접 데이터와 스키마를 정의하여 DataFrame을 생성하는 방식**입니다.

    ```python
    from pyspark.sql import SparkSession

    spark = SparkSession.builder.appName("DataFrameExample").getOrCreate()

    data = [("철수", 25), ("영희", 30)]
    columns = ["name", "age"]

    df = spark.createDataFrame(data, columns)
    df.show()
    ```

    출력 결과:

    ```
    +-----+---+
    | name|age|
    +-----+---+
    | 철수| 25|
    | 영희| 30|
    +-----+---+
    ```
    <br>

    2️⃣ Creating DataFrames – SQL 코드       
     
    SQL 문법을 활용하여 DataFrame을 조작하려면,  
    먼저 해당 DataFrame을 **임시 뷰(View)** 로 등록해야 합니다.

    ```python
    df.createOrReplaceTempView("people")

    # SQL 쿼리 실행
    spark.sql("SELECT name FROM people WHERE age > 25").show()
    ```

    → 이 방식은 DataFrame을 **데이터베이스 테이블처럼 활용**할 수 있게 해줍니다.

    <br>

    3️⃣ Creating DataFrames From File – DSL 코드      

    실무에서는 외부 파일(CSV, JSON 등)로부터 데이터를 읽어와 DataFrame을 생성하는 경우가 일반적입니다.

    ```python
    df = spark.read.csv("people.csv", header=True, inferSchema=True)
    df.show()
    ```

    *   `header=True`: 파일의 첫 줄을 컬럼 이름으로 인식
        
    *   `inferSchema=True`: 데이터 타입을 자동으로 추론하여 스키마 구성     

    <br>

    4️⃣ Creating DataFrames From File – SQL 코드

    파일 데이터를 SQL 쿼리로 다루기 위해서는  
    먼저 DataFrame으로 로딩한 뒤 **임시 뷰로 등록**한 후 SQL 문을 실행합니다.

    ```python
    df = spark.read.csv("people.csv", header=True, inferSchema=True)
    df.createOrReplaceTempView("people")

    spark.sql("SELECT * FROM people WHERE age >= 30").show()
    ```

    <br>

    5️⃣ From Spark Data Sources

    Spark는 다양한 외부 데이터 소스를 지원합니다.  
    아래는 자주 사용하는 포맷별 연결 예시입니다:

    | 포맷    | 예시 코드                                 |
    | ------- | ----------------------------------------- |
    | JSON    | `spark.read.json("data.json")`            |
    | Parquet | `spark.read.parquet("data.parquet")`      |
    | JDBC    | `spark.read.jdbc(url, table, properties)` |
    | Hive    | `spark.sql("SELECT * FROM hive_table")`   |

    <br>

    지금까지 배운 내용을 요약하면 다음과 같습니다:

    > ✅ 데이터를 직접 정의하거나  
    > 📁 외부 파일로부터 불러오거나  
    > 🗃️ SQL 문법을 활용해 뷰로 등록한 후  
    > → 다양한 방식으로 DataFrame을 생성하고 분석할 수 있습니다.


<br>

### 2.2 데이터 조회 및 조건 처리

***

**- 데이터 확인 (Inspect Data)**   

**✅ DSL 방식**

```python
df.show(5)  # 앞에서 5개 행 출력
df.printSchema()  # 컬럼 타입 및 구조 출력
df.describe().show()  # 통계 요약 정보 출력
```

**✅ SQL 방식**

```python
df.createOrReplaceTempView("people")
spark.sql("SELECT * FROM people LIMIT 5").show()
```         


→ 데이터를 간단히 조회하거나 구조를 확인할 때 유용하게 활용됩니다.

<br>

**- 중복값 처리 (Duplicate Values)**        

✅ DSL 방식

```python
df.dropDuplicates().show()  # 전체 행 기준으로 중복 제거
df.dropDuplicates(["name"]).show()  # name 컬럼 기준 중복 제거
```

#### ✅ SQL 방식

```sql
SELECT DISTINCT name FROM people
```

→ 중복된 데이터를 제거할 때는 `dropDuplicates()` 또는 `DISTINCT`를 사용합니다.      

<br>

**- SELECT 쿼리**    
  - SELECT (기본)       
    
    ✅ DSL 방식

    ```python
    df.select("name", "age").show()
    ```

    ✅ SQL 방식

    ```sql
    SELECT name, age FROM people
    ```

    → 특정 컬럼만 선택적으로 조회할 수 있으며, DSL과 SQL 방식 모두 직관적으로 사용할 수 있습니다.
    
  - SELECT with Expressions & Filters    
    
    ✅ DSL 방식

    ```python
    df.select(df.name, df.age + 1).show()  # 나이에 +1 계산 컬럼 추가
    df.filter(df.age > 25).show()  # 나이가 25 초과인 데이터 필터링
    ```

    ✅ SQL 방식

    ```sql
    SELECT name, age + 1 AS age_plus
    FROM people
    WHERE age > 25
    ```

    → 계산식과 조건을 함께 사용하여 데이터프레임을 동적으로 조작할 수 있습니다. 

  - When, ISIN 조건 (DSL)       
    
    ✅ DSL 방식 (조건 분기 처리)

    ```python
    from pyspark.sql.functions import when

    df.select("name", "age",
            when(df.age >= 30, "O").otherwise("X").alias("is_adult")).show()
    ```

    → `when(condition, value)` 구문은 if-else와 유사한 방식으로 조건 분기를 구현할 수 있습니다.

    ✅ DSL 방식 (ISIN: 특정 값 포함 여부 확인)

    ```python
    df.filter(df.city.isin("서울", "부산")).show()
    ```

  - CASE WHEN, IN 조건 (SQL)

    ```sql
    SELECT name, age,
    CASE WHEN age >= 30 THEN 'O' ELSE 'X' END AS is_adult
    FROM people
    WHERE city IN ('서울', '부산')
    ```

    → SQL에서도 `CASE WHEN`을 활용하여 조건 분기를 처리하고, `IN` 연산자를 통해 특정 값 포함 여부를 간편하게 확인할 수 있습니다.

<br>

### 2.3 문자열 처리 및 컬럼 조작

***

**- 문자열 조건 처리**
  - Like, STARTSWITH, ENDSWITH (DSL)
    
    ```python
    # like: 문자열 패턴 포함 여부 확인
    df.filter(df.name.like("철%")).show()  
    # → '철'로 시작하는 이름 조회

    # startsWith: 특정 문자열로 시작하는 값 필터링
    df.filter(df.city.startswith("서")).show()  
    # → 예: '서울'

    # endsWith: 특정 문자열로 끝나는 값 필터링
    df.filter(df.city.endswith("산")).show()  
    # → 예: '부산'
    ```

  - Like, STARTSWITH, ENDSWITH (SQL)
    
    ```sql
    SELECT * FROM people
    WHERE name LIKE '철%'        -- '철'로 시작하는 이름

    SELECT * FROM people
    WHERE city LIKE '%산'        -- '산'으로 끝나는 도시

    SELECT * FROM people
    WHERE city LIKE '%경%'       -- '경'이 포함된 모든 도시
    ```

    💡 참고: `%`는 와일드카드 문자로, **임의의 문자 0개 이상**을 의미합니다.

    *   `'철%'` → '철'로 시작하는 문자열
        
    *   `'%산'` → '산'으로 끝나는 문자열
        
    *   `'%경%'` → '경'이 포함된 문자열

<br>

**- 문자열 추출 및 범위 조건 처리**
  - Substring, Between (DSL)
    
    ```python
    from pyspark.sql.functions import substring

    # 이름에서 앞 글자 2개 추출
    df.select(df.name, substring(df.name, 1, 2).alias("short_name")).show()

    # 나이가 25 ~ 30 사이인 행 필터링
    df.filter(df.age.between(25, 30)).show()
    ```

    *   `substring(컬럼, 시작위치, 길이)`
        
        *   시작 위치는 **1부터 시작**하며, SQL과 동일한 규칙을 따릅니다.
            
  - Substring, Between (SQL)
    
    ```sql
    SELECT name, SUBSTRING(name, 1, 2) AS short_name
    FROM people

    SELECT * FROM people
    WHERE age BETWEEN 25 AND 30
    ```

정리하자면,

*   문자열 조건 필터링에는 `like`, `startswith`, `endswith`
    
*   문자열 조작에는 `substring`
    
*   범위 조건 지정에는 `between`
    

이러한 방식으로 분류하여 활용하면 효율적인 조건 처리 및 추출이 가능합니다.

<br>

**- 컬럼 이름 변경 및 삭제**    

  - Update & Remove Columns (DSL)   

    ① 컬럼 이름 변경 – `withColumnRenamed()`

    ```python
    df.withColumnRenamed("age", "user_age").show()
    ```

    *   `"age"` 컬럼의 이름을 `"user_age"`로 변경합니다.
        
    *   주로 **컬럼명을 보다 직관적으로 수정하거나**,  
        **다른 테이블과 조인 시 컬럼 이름 충돌을 방지하기 위한 목적**으로 사용됩니다.
    
    ② 컬럼 삭제 – `drop()`

    ```python
    df.drop("city").show()
    ```

    *   `"city"` 컬럼을 제거합니다.
        
    *   복수의 컬럼을 제거하고자 할 경우에는 `.drop("col1", "col2")`와 같이 사용이 가능합니다.

  - Update & Remove Columns (SQL)    
        
    > SQL에서는 컬럼 이름 변경 및 삭제가 직접적으로 제공되지는 않으며,  
    > 일반적으로는 **`SELECT` 문을 통해 우회적으로 처리**합니다.

    <br>

    ① 컬럼 이름 변경 (AS 키워드 사용)

    ```sql
    SELECT name, age AS user_age
    FROM people
    ```

    *   `age` 컬럼에 `user_age`라는 별칭을 지정합니다.
        
    *   주의할 점은, **원본 DataFrame 자체의 컬럼명은 변경되지 않습니다.**
        
    ② 컬럼 제거 (불필요한 컬럼 제외하여 선택)

    ```sql
    SELECT name, age
    FROM people
    ```

    *   `"city"` 컬럼을 제거하려면, **조회 시 해당 컬럼을 선택하지 않으면 됩니다.**
    
  - ➕ 컬럼 추가 – DSL 방식

    ✅ `withColumn()` 메서드 활용

    ```python
    from pyspark.sql.functions import col

    df.withColumn("age_plus_5", col("age") + 5).show()
    ```

    *   기존 컬럼을 가공하여 새로운 컬럼을 추가할 수 있습니다.
        
    *   수치 연산, 조건문, 문자열 결합 등 다양한 형태의 로직을 적용할 수 있습니다.
        

    예시: 이름과 도시를 결합하여 하나의 문자열로 구성

    ```python
    from pyspark.sql.functions import concat_ws

    df.withColumn("full_info", concat_ws(" - ", df.name, df.city)).show()
    ```

    출력 예시:

    ```
    +-----+---+----+--------------+
    |name |age|city|   full_info |
    +-----+---+----+--------------+
    |철수 |25 |서울|철수 - 서울   |
    |영희 |30 |부산|영희 - 부산   |
    +-----+---+----+--------------+
    ```

<br>

정리하자면,

| 작업 유형      | DSL 방식                   | SQL 방식              |
| -------------- | -------------------------- | --------------------- |
| 컬럼 이름 변경 | `withColumnRenamed()`      | `AS`                  |
| 컬럼 삭제      | `drop()`                   | SELECT 문에서 제외    |
| 컬럼 추가      | `withColumn()` + 가공 수식 | SELECT 문에 수식 삽입 |
 

<br>

### 2.4 집계, 필터링, 정렬

***

**- 그룹별 집계**
  - Group By, Count (DSL)
    
    ```python
    df.groupBy("city").count().show()
    ```

    *   `"city"` 컬럼을 기준으로 그룹을 나눈 후,  
        각 그룹별 **행의 개수(count)** 를 계산합니다.
        
    *   다른 집계 함수들과 함께 사용할 수도 있습니다:
        

    ```python
    from pyspark.sql.functions import avg, max, min, count

    df.groupBy("city").agg(
        count("*").alias("cnt"),
        avg("age").alias("avg_age"),
        max("age").alias("max_age")
    ).show()
    ```

  - Group By, Count (SQL)

    ```sql
    SELECT city, COUNT(*) AS cnt, AVG(age) AS avg_age, MAX(age) AS max_age
    FROM people
    GROUP BY city
    ```

    *   SQL에서도 `GROUP BY` 구문과 다양한 집계 함수를 함께 사용하여  
        동일한 결과를 얻을 수 있습니다.
        
<br>

**- 조건 필터링**
  - Filter (DSL)
    
    ```python
    df.filter(df.age > 25).show()

    # 복수 조건
    df.filter((df.age > 25) & (df.city == "서울")).show()
    ```

    *   **AND 조건은 `&`**, **OR 조건은 `|`** 으로 표현하며,  
        연산자 사용 시 괄호로 명확하게 감싸야 오류를 방지할 수 있습니다.
        
    *   `==`, `!=` 등 다양한 조건 연산자가 지원됩니다.
        
  - Filter (SQL)

    ```sql
    SELECT * FROM people
    WHERE age > 25 AND city = '서울'
    ```

    *   SQL에서는 `AND`, `OR`, `NOT` 등의 키워드를 활용하여  
        복잡한 조건을 손쉽게 조합할 수 있습니다.
        
<br>

**- 정렬**
  - Sort, OrderBY (DSL)

    ```python
    df.orderBy("age").show()  # 오름차순 정렬
    df.orderBy(df.age.desc()).show()  # 내림차순 정렬
    ```

    *   `.orderBy()`는 하나 이상의 컬럼을 기준으로 정렬이 가능하며,  
        `desc()`를 사용하면 내림차순 정렬을 수행할 수 있습니다.
        

    ```python
    df.orderBy("city", df.age.desc()).show()
    ```

  - Sort, OrderBY (SQL)

    ```sql
    SELECT * FROM people
    ORDER BY age ASC

    SELECT * FROM people
    ORDER BY city ASC, age DESC
    ```

    *   SQL의 `ORDER BY` 구문도 다중 컬럼 정렬을 지원하며,  
        기본은 오름차순(`ASC`), 명시적으로 `DESC`를 지정하면 내림차순이 됩니다.
        
✅ **Tip**  
정렬 작업은 데이터를 직관적으로 살펴보는 데 유용하지만,  
**대용량 데이터셋에서는 성능 저하를 유발할 수 있으므로 주의가 필요**합니다.  
특히 `.show()` 전에 불필요하게 정렬을 수행하는 습관은 지양하는 것이 좋습니다.

<br>
지금까지 배운 내용을 정리하면 다음과 같습니다:

| 기능        | DSL 방식           | SQL 방식   |
| ----------- | ------------------ | ---------- |
| 그룹 집계   | `.groupBy().agg()` | `GROUP BY` |
| 조건 필터링 | `.filter()`        | `WHERE`    |
| 정렬        | `.orderBy()`       | `ORDER BY` |

<br>

### 2.5 결측값 처리

***

*   데이터가 **비어 있거나 누락된 상태**를 의미합니다.
    
*   예시: `NULL`, `NaN`, `None` 등
    
*   결측값이 존재할 경우 평균 계산, 조건 필터링 등의 연산에서 오류가 발생할 수 있으므로  
    **분석에 앞서 반드시 적절한 처리가 필요합니다.**

**- 결측값 처리 및 값 치환**
  - Missing & Replacing Values (DSL)
    
    ① 결측값 확인

    ```python
    df.select([count(when(col(c).isNull(), c)).alias(c) for c in df.columns]).show()
    ```

    *   각 컬럼별로 `null` 값이 몇 개인지 확인할 수 있는 코드입니다.
        
    *   결측 데이터의 분포를 파악하는 데 유용합니다.
        
    ② 결측값 제거 – `dropna()`

    ```python
    df.na.drop().show()  # 결측값이 포함된 행 전체 삭제

    df.na.drop(subset=["age", "city"]).show()  # 특정 컬럼 기준으로만 삭제
    ```

    *   기본적으로는 결측값이 존재하는 모든 행을 제거하며,
        
    *   특정 컬럼만 기준으로 지정할 수도 있습니다.
        
    ③ 결측값 채우기 – `fillna()`

    ```python
    df.na.fill(0).show()  # 숫자형 컬럼 전체에 0 채움

    df.na.fill({"city": "미정", "age": 0}).show()  # 컬럼별로 다르게 채우기
    ```

    *   `fillna()`를 사용하면 결측 데이터를 특정 값으로 대체할 수 있으며,
        
    *   **컬럼별로 다른 값을 지정하여 세밀하게 조정**할 수 있습니다.
        
    ④ 특정 값 대체 – `replace()`

    ```python
    df.na.replace("서울", "SEOUL").show()
    df.na.replace(["부산", "대전"], "기타").show()
    ```

    *   결측값이 아닌 일반 값의 치환에도 사용할 수 있으며,
        
    *   다수의 값을 한 번에 변경할 수 있습니다.
        

  - Missing & Replacing Values (SQL)

    SQL에서는 결측값을 처리하기 위해 주로 **`IS NULL`, `IS NOT NULL`, `COALESCE()`** 등을 활용합니다.

    <br>

    ① 결측값 확인 및 필터링

    ```sql
    SELECT * FROM people
    WHERE city IS NULL

    SELECT * FROM people
    WHERE age IS NOT NULL
    ```

    *   `IS NULL`을 통해 누락된 데이터를 조회할 수 있고,
        
    *   `IS NOT NULL`을 사용하여 결측값을 제외한 데이터를 필터링할 수 있습니다.
        
    ② 결측값 대체 – `COALESCE()`

    ```sql
    SELECT name, COALESCE(city, '미정') AS city_fixed
    FROM people
    ```

    *   `COALESCE(A, B)`는 **A가 NULL일 경우 B를 반환**합니다.
        
    *   여러 개의 대체 값을 순차적으로 지정할 수도 있습니다.
        
    ③ 특정 값 바꾸기 – `CASE WHEN`

    ```sql
    SELECT name,
      CASE 
        WHEN city = '서울' THEN 'SEOUL'
        ELSE city
      END AS city_eng
    FROM people
    ```

    *   `CASE WHEN` 구문을 활용하면 **값을 조건에 따라 유연하게 변환**할 수 있습니다.
        
    *   단일 조건뿐 아니라 복잡한 다중 조건도 적용 가능합니다.

📌 요약 정리

| 기능         | DSL 방식                   | SQL 방식                |
| ------------ | -------------------------- | ----------------------- |
| 결측값 제거  | `.na.drop()`               | `WHERE col IS NOT NULL` |
| 결측값 대체  | `.na.fill()`, `COALESCE()` | `COALESCE(col, '값')`   |
| 특정 값 치환 | `.na.replace()`            | `CASE WHEN` 문          |

