# 금융 텍스트 데이터를 통한 WordCount

📘 1\. 실습 주제 개요
---------------

이번 실습은 **PyFlink를 활용한 스트리밍 단어 수 세기(WordCount)** 를 구현하는 것이다.  
Flink는 대규모 스트림 데이터를 분산 병렬로 처리할 수 있는 프레임워크이며, PyFlink는 그 기능을 Python 언어로 활용할 수 있도록 하는 인터페이스이다.

실습에서는 Pandas를 사용하여 로컬 CSV 파일로부터 정적 데이터를 로드하고, PyFlink의 `StreamExecutionEnvironment`를 통해 다음과 같은 처리 과정을 구성한다:

> CSV(news\_text 컬럼) → 문자열 스트림 → 단어 분리 및 소문자화 → 단어별 그룹핑 → 빈도수 누적 → 출력

이 실습을 통해 다음과 같은 개념과 기술을 습득할 수 있다:

*   Pandas와 PyFlink 연동 방식 이해
    
*   Flink의 핵심 연산자인 `map`, `flat_map`, `key_by`, `reduce`의 처리 흐름
    
*   단어 수준의 스트림 처리 구조 구성
    
*   병렬성 설정 및 실행 환경 제어
    

실무에서는 이 구조를 기반으로 뉴스 요약, 키워드 추출, 사용자 로그 분석 등의 스트리밍 분석 애플리케이션으로 확장할 수 있다.

<br>
<br>

🛠️ 2\. 코드 구조 및 흐름 해설 + 실행 결과 예시 및 해설
-------------------------------------

### 🔧 1단계: 실행 환경 설정

```python
env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(2)
```

*   Flink 실행 환경을 생성하고, 병렬성을 2로 설정함
    
*   병렬성이란 각 연산이 몇 개의 인스턴스로 병렬 실행되는지를 의미하며, 클러스터에서는 물리적 task slot 수와 관련됨
    
*   병렬성을 조정하면 성능 테스트나 파티션 분산 효과를 실험할 수 있음
    

<br>

### 📄 2단계: 입력 데이터 로딩 및 전처리

```python
df = pd.read_csv("../data/data.csv")
news_texts = df["news_text"].dropna().tolist()
```

*   Pandas를 사용하여 CSV 파일을 불러온 뒤, `news_text` 컬럼에서 결측값을 제거하고 리스트로 변환함
    
*   Flink는 Pandas의 DataFrame을 직접 처리하지 않기 때문에, 리스트로 전처리하여 Flink에 입력해야 함
    

예시 입력:

```python
["Breaking news: Stocks fall", "Investors worry about inflation", "Markets rebound slightly"]
```

<br>

### 🌊 3단계: PyFlink 스트림으로 변환

```python
text_stream = env.from_collection(news_texts, type_info=Types.STRING())
```

*   리스트 형태의 문자열 데이터를 Flink의 DataStream으로 변환
    
*   각 요소는 하나의 "텍스트 문장"으로 간주됨
    
*   `Types.STRING()`을 통해 스트림 내부 데이터 타입을 명시
    

<br>

### 🔄 4단계: WordCount 처리 파이프라인

```python
word_count = (text_stream
    .map(lambda text: [(word.lower(), 1) for word in text.split()], output_type=Types.LIST(...))
    .flat_map(lambda words: words, output_type=Types.TUPLE(...))
    .key_by(lambda x: x[0])
    .reduce(lambda a, b: (a[0], a[1] + b[1])))
```

#### 🧩 `.map(...)`

*   각 문장을 단어로 분리하고, 모든 단어를 소문자로 정규화한 뒤 `(단어, 1)` 형식의 튜플 리스트로 반환
    
*   예: `"Stocks fall"` → `[("stocks", 1), ("fall", 1)]`
    

#### 🧩 `.flat_map(...)`

*   앞 단계에서 반환된 리스트를 풀어헤쳐서 스트림 요소로 분리
    
*   결과: `"Stocks fall"` → `("stocks", 1)`, `("fall", 1)` 개별 단위로 전개
    

#### 🧩 `.key_by(...)`

*   단어를 기준으로 그룹화 (`keyBy`는 스트림 분할 연산)
    
*   같은 단어는 같은 인스턴스로 라우팅됨
    

#### 🧩 `.reduce(...)`

*   누적 함수로, 같은 단어의 빈도수를 합산
    
*   `("stocks", 1), ("stocks", 1)` → `("stocks", 2)`
    

<br>

### 📤 5단계: 결과 출력 및 실행

```python
word_count.print()
env.execute("Finance News WordCount")
```

*   처리된 단어 빈도 결과를 터미널로 출력
    
*   `env.execute(...)`는 Flink 작업 실행의 필수 호출로, DAG을 구성한 후 실행함
    

<br>

### 🖥️ 실행 결과 예시

입력:

```python
["Market falls sharply", "Market recovers"]
```

출력 (순서는 병렬 처리 결과에 따라 다를 수 있음):

```
(market, 2)
(falls, 1)
(sharply, 1)
(recovers, 1)
```

<br>
<br>

⚙️ 3\. 전체 코드 + 상세 주석
--------------------

```python
import pandas as pd
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common.typeinfo import Types

def main():
    # Flink 스트림 실행 환경 생성 (작업의 시작점이 되는 객체)
    env = StreamExecutionEnvironment.get_execution_environment()

    # 병렬성 설정: 작업을 병렬로 실행할 수 있는 인스턴스 수를 2로 지정
    env.set_parallelism(2)

    # CSV 파일을 Pandas로 읽어옴 (news_text 컬럼 포함)
    df = pd.read_csv("../data/data.csv")

    # news_text 컬럼에서 결측값 제거 후, 리스트 형태로 변환
    news_texts = df["news_text"].dropna().tolist()

    # news_text 리스트를 Flink의 스트림으로 변환 (각 요소는 문자열 문장)
    text_stream = env.from_collection(
        news_texts,
        type_info=Types.STRING()  # 각 요소의 타입을 문자열로 명시
    )

    # WordCount 파이프라인 구성:
    # 1. 문장을 단어 단위로 나누고
    # 2. 소문자로 정규화 후 (단어, 1) 튜플로 매핑
    # 3. 단어별로 그룹핑하고
    # 4. 빈도수를 누적 합산
    word_count = (
        text_stream
        # map: 문장을 단어로 나누고 (word.lower(), 1) 형식의 리스트 반환
        .map(
            lambda text: [(word.lower(), 1) for word in text.split()],
            output_type=Types.LIST(
                Types.TUPLE([Types.STRING(), Types.INT()])
            )
        )

        # flat_map: 리스트를 개별 튜플로 분해하여 스트림 요소로 분리
        .flat_map(
            lambda words: words,
            output_type=Types.TUPLE([Types.STRING(), Types.INT()])
        )

        # key_by: 첫 번째 요소(단어)를 기준으로 그룹핑
        .key_by(lambda x: x[0])

        # reduce: 같은 단어의 카운트를 누적 합산
        .reduce(lambda a, b: (a[0], a[1] + b[1]))
    )

    # 결과 출력: 각 단어별 빈도수를 콘솔에 출력
    word_count.print()

    # Flink 파이프라인 실행 (작업 DAG 실행 시작)
    env.execute("Finance News WordCount")

# Python 파일 직접 실행 시 main() 함수 호출
if __name__ == "__main__":
    main()
```

<br>
<br>

📚 4\. 추가 설명 및 실무 팁
-------------------

### ✅ 실무에서 WordCount가 갖는 의미

WordCount는 단순한 예제로 보일 수 있지만, 실제 데이터 처리 시스템에서는 **텍스트 기반 이벤트의 집계**, **로그 분석**, **뉴스 키워드 추출**, **고객 발화 요약**, **해시태그 통계** 등으로 직접 활용된다.  
이번 실습은 특히 다음과 같은 실무 시나리오로 쉽게 확장할 수 있다:

| 실무 시나리오 | WordCount 응용 방식 |
| --- | --- |
| 뉴스 기사 키워드 요약 | 제목, 본문에서 단어 추출 및 카운트 |
| 실시간 로그 키워드 분석 | "에러", "경고" 등의 등장 횟수 계산 |
| SNS 해시태그 트렌드 분석 | `#태그` 단어 카운트 |
| 챗봇 사용자 발화 분석 | 주요 키워드 추출 및 응답 맞춤 |

<br>

### ⚠️ 자주 발생하는 실수 및 주의사항

| 실수 | 설명 및 해결 방법 |
| --- | --- |
| ❌ 문자열 파싱 오류 | `.split()`만 사용할 경우 구두점 포함됨 → 정규식 or `nltk.word_tokenize()` 사용 권장 |
| ❌ 데이터 타입 오류 | PyFlink는 `output_type` 명시 필수 → `Types.TUPLE(...)` 반드시 지정해야 |
| ❌ 결과가 안 나옴 | `env.execute()` 누락 시 Flink DAG 실행이 되지 않음 |
| ❌ 병렬성 증가 후 출력 순서 꼬임 | `key_by` 이후 파티셔닝됨 → 순서 보장 없음, 정렬 필요 시 후처리 필요 |

<br>

### 💼 실무 확장 방향

#### 1\. **Kafka + Flink + Elasticsearch 연동**

*   Kafka에서 실시간 뉴스/로그 소비
    
*   Flink로 실시간 WordCount 처리
    
*   Elasticsearch에 저장 후 Kibana로 시각화
    

#### 2\. **불용어 제거 및 형태소 분석**

*   `lambda text: [(word, 1) for word in text.split()]` 대신  
    → `from konlpy.tag import Okt` 또는 `nltk`로 품사 분석 + 불용어 제거 적용
    

#### 3\. **PyFlink Table API로 전환**

*   DataStream 대신 SQL 기반 API로 처리
    
*   더 강력한 집계, 필터링, 윈도우 연산 등 가능
    

#### 4\. **출력 결과 저장**

*   `word_count.print()` 대신 `.add_sink(...)` 사용하여 CSV, PostgreSQL, Kafka 등으로 전송
    

<br>

### 🧠 성능 최적화를 위한 팁

| 조치 | 기대 효과 |
| --- | --- |
| `env.set_parallelism(n)` 조절 | 분산 처리 속도 개선 |
| 데이터 전처리 후 스트림 전달 | Flink 연산량 감소 |
| 중간 단계 병합 (flat\_map ↔ map) | 연산 단계 축소로 처리 시간 단축 |
| Key Skew 방지 | 특정 단어(예: "the") 집중 발생 시 파티셔닝 불균형 유의 |

<br>

### ✅ 마무리 요약

*   이 실습은 PyFlink 기반의 실시간 스트리밍 데이터 처리 흐름을 체험하는 데 매우 효과적이다.
    
*   핵심 연산 (`map`, `flat_map`, `key_by`, `reduce`)의 구조를 파악하면 실시간 집계 및 키워드 분석 시스템 구현이 가능하다.
    
*   실무 적용을 위해 Kafka와 연동하거나 결과를 외부 DB/검색엔진에 저장하는 구조로 확장할 수 있다.
    
