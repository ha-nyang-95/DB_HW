# Vue 환경에서의 스트리밍 데이터 파이프라인 구축

📄 **초록(Abstract)**

본 연구는 Kafka와 Apache Flink를 활용한 실시간 뉴스 데이터 스트리밍 파이프라인의 설계 및 구현을 통해,           
대용량 뉴스 데이터를 자동 수집·분석·저장하는 엔드 투 엔드 처리 구조를 제안한다.           
뉴스 데이터는 RSS 피드로부터 실시간으로 수집되며, Kafka Producer를 통해 메시지 큐에 전송된다.           
이후 Flink 기반 Kafka Consumer가 해당 데이터를 스트림 형태로 소비하고,              
OpenAI의 GPT 모델을 활용하여 주요 키워드 추출, 의미 기반 임베딩 생성, 카테고리 분류 등 자연어 기반 전처리를 수행한다.            
전처리된 결과는 PostgreSQL에 저장되어 추후 검색, 시각화, 인사이트 도출 등 다양한 응용이 가능하다.                   
본 시스템은 **실시간성과 확장성을 모두 고려한 구조**로 설계되었으며,            
데이터 수집에서부터 AI 기반 분석, 저장까지의 흐름을 자동화함으로써,                 
뉴스 데이터의 실시간 활용 가능성을 높이고 정보 기반 의사결정의 정밀도를 향상시키는 데 기여할 수 있다.

### ✅ 전체 구성

1.  📘 **실습 주제 개요 (이론, 목적, 왜 배우는지)**
    
2.  🛠️ **코드 구조 및 흐름 해설 + 실행 결과 예시 및 해설**
    
3.  ⚙️ **전체 코드 + 상세 주석**
    
4.  📚 **추가 설명 및 실무 팁 (자주 하는 실수, 심화 방향 등)**
    

<br>

📘 1. 실습 주제 개요
==============

**Kafka + Flink를 활용한 실시간 뉴스 스트리밍 데이터 파이프라인 구축**


💡 실습 개요
--------

본 실습의 목표는 **실시간으로 뉴스 데이터를 수집, 처리, 저장하는 데이터 파이프라인을 설계하고 구현**하는 데 있다.  
이를 위해 **Kafka**를 통해 데이터 스트리밍 채널을 구성하고,  
**Apache Flink**를 이용하여 데이터를 실시간으로 처리한 후,  
**PostgreSQL**에 저장하는 엔드 투 엔드 흐름을 실습한다.

이러한 실습은 **데이터 엔지니어링, 실시간 분석 시스템, 자연어 처리 기반 뉴스 분석 서비스**를 위한  
핵심 기초 설계 역량을 길러주는 데 목적이 있다.


🎯 학습 목적
--------

*   **Kafka의 동작 원리**와 Producer-Consumer 모델의 이해
    
*   **RSS 피드를 크롤링하여 실시간 데이터 수집**하기
    
*   **Flink를 활용해 실시간 스트리밍 처리 환경을 구성**하고, Kafka로부터 데이터를 받아 처리하기
    
*   **OpenAI API를 활용한 전처리 및 임베딩, 키워드 추출, 카테고리 분류 실습**
    
*   **최종적으로 정제된 데이터를 PostgreSQL에 저장**하는 전 과정을 이해 및 구현
    


📌 실습을 통해 배우는 핵심 역량
-------------------

| 역량 항목                 | 설명                                                           |
| ------------------------- | -------------------------------------------------------------- |
| 실시간 데이터 수집        | Kafka Producer를 활용해 뉴스 데이터를 실시간으로 수집하고 전송 |
| 분산 메시징 시스템 이해   | Kafka의 토픽, 파티션, 그룹 아이디 등 핵심 개념 체득            |
| 스트리밍 처리 엔진 활용   | Flink를 이용한 실시간 데이터 소비 및 처리 로직 구현            |
| AI 기반 전처리 적용       | GPT API 기반 키워드 추출, 임베딩, 카테고리 분류 경험           |
| 데이터베이스 연동 및 저장 | 처리된 결과를 PostgreSQL에 저장하는 실무 수준의 저장 로직 구현 |


🏗️ 전체 시스템 아키텍처
---------------

```
┌────────────────────┐
│   RSS 뉴스 피드      │
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│ Kafka Producer     │
│ (rss_producer_test)│
└────────┬───────────┘
         ▼
┌────────────────────┐
│   Kafka Broker     │
│    (토픽: news)     │
└────────┬───────────┘
         ▼
┌───────────────────────────────┐
│      Flink Kafka Consumer     │
│ (consumer_flink + preprocess) │
└────────┬──────────────────────┘
         ▼
┌────────────────────────────────┐
│ PostgreSQL (news_article 테이블) │
└────────────────────────────────┘
```

<br>
<br>

🛠️ 2. 코드 구조 및 흐름 해설 + 실행 결과 예시 및 해설
====================================

🔧 전체 흐름 개요
-----------

이 프로젝트는 다음과 같은 **3단계 구조**로 작동한다:

| 단계  | 설명                                                      | 주요 파일              |
| ----- | --------------------------------------------------------- | ---------------------- |
| 1단계 | RSS에서 뉴스 데이터를 실시간 수집 후 Kafka에 전송         | `rss_producer_test.py` |
| 2단계 | Kafka에서 실시간 메시지를 Flink가 수신 및 처리            | `consumer_flink.py`    |
| 3단계 | 뉴스 본문 분석 및 DB 저장 (키워드, 임베딩, 카테고리 포함) | `preprocess.py`        |


🔁 각 코드 흐름 상세 설명
----------------

### ① **`rss_producer_test.py` – Kafka Producer**

#### 🔍 주요 흐름 설명

| 순서 | 기능                                                                        |
| ---- | --------------------------------------------------------------------------- |
| 1    | `feedparser`로 RSS 피드 파싱 (뉴스 제목, 링크, 작성일 등)                   |
| 2    | 각 뉴스 링크에 접속하여 본문 및 기자명 크롤링 (`requests`, `BeautifulSoup`) |
| 3    | 수집한 데이터를 JSON 형태로 Kafka에 전송                                    |
| 4    | 1초 간격으로 다음 뉴스 처리 (`time.sleep(1)`)                               |

#### ✅ 핵심 포인트

*   Kafka Producer는 `value_serializer`로 JSON 직렬화 설정
    
*   뉴스 본문이 없을 경우 `[본문 없음]` 처리
    
*   카프카 전송 확인용 로그 출력:  
    `print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Sent: {title}")`
    

<br>

### ② **`consumer_flink.py` – Kafka Consumer + Flink 처리**

#### 🔍 주요 흐름 설명

| 순서 | 기능                                                    |
| ---- | ------------------------------------------------------- |
| 1    | Kafka로부터 실시간 뉴스 메시지를 수신                   |
| 2    | 수신된 메시지를 `process_and_save()`에 전달             |
| 3    | `preprocess.py`를 통해 키워드/임베딩/카테고리 자동 생성 |
| 4    | 모든 결과를 PostgreSQL에 저장                           |

#### ✅ 핵심 포인트

*   Flink 스트림 환경 설정: `StreamExecutionEnvironment.get_execution_environment()`
    
*   Kafka Connector JAR 파일을 코드 내에서 명시적으로 로드
    
*   각 뉴스 콘텐츠에 대해 OpenAI 기반 전처리 실행
    
*   DB 저장은 psycopg2 라이브러리를 이용한 SQL 실행 방식

<br>

### ③ **`preprocess.py` – 전처리 유닛 모듈**

#### 🔍 전처리 세부 흐름

| 기능          | 설명                                                      |
| ------------- | --------------------------------------------------------- |
| 텍스트 정제   | 최대 5000 토큰 이하로 자르기 (`tiktoken` 활용)            |
| 키워드 추출   | GPT를 통해 핵심 명사 5개 추출                             |
| 임베딩 생성   | GPT 임베딩 API (`text-embedding-3-small`) 활용            |
| 카테고리 분류 | GPT로 본문을 분류 항목 중 하나로 매핑 (예: 정치, 경제 등) |

#### ✅ 핵심 포인트

*   `tiktoken`을 통해 OpenAI API 토큰 제한을 사전 방지
    
*   모든 응답은 GPT API 사용 → 결과의 품질이 NLP보다 높음
    
*   잘못된 응답에 대한 fallback 처리: 카테고리 목록에 없으면 `"미분류"`

<br>

💡 실행 결과 예시
-----------

실제 실행 시, 다음과 같은 콘솔 로그가 출력됨:

```bash
[2025-04-18 16:32:19] Sent: "中, 1분기 성장률 5.3%...예상 상회"
[저장 완료] 中, 1분기 성장률 5.3%...예상 상회
```

*   **Sent**: Kafka로 뉴스가 전송되었음을 의미
    
*   **저장 완료**: 전처리 및 DB 저장까지 성공한 경우
    

만약 본문이 없거나 OpenAI 처리 중 오류가 생기면 다음과 같은 예외 메시지도 출력됨:

```bash
[본문/기자 크롤링 오류] https://... → 'NoneType' object has no attribute ...
[처리 오류] JSONDecodeError: Expecting value: line 1 column 1 (char 0)
[DB 오류] duplicate key value violates unique constraint ...
```

<br>

⚙️ 3. 전체 코드 + 상세 주석
===================

📄 \[1\] `rss_producer_test.py`
-------------------------------

**Kafka로 RSS 뉴스를 실시간 전송하는 Producer**

```python
# RSS 피드 파싱 및 웹 크롤링용 라이브러리
import feedparser
import requests
from bs4 import BeautifulSoup

# Kafka Producer 라이브러리
from kafka import KafkaProducer

# 시스템, JSON 처리용
import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv

# .env 환경변수 로딩 (Kafka 설정 등)
load_dotenv()

# Kafka 브로커 주소
KAFKA_BROKER = "localhost:9092"

# Kafka 토픽 이름
TOPIC = "news"

# Kafka Producer 생성 (JSON 직렬화 형식 설정)
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8')
)

# 사용할 뉴스 RSS 피드 주소 (매일경제 사회면)
RSS_FEED_URL = "https://www.mk.co.kr/rss/50200011/"

# 뉴스 본문과 기자명 추출 함수
def extract_article_text(url):
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")

        content = ""
        wrapper = soup.find("div", class_="news_cnt_detail_wrap")

        # 본문 내용이 있는 경우
        if wrapper:
            paragraphs = wrapper.find_all("p")
            if paragraphs:
                content = "\n\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
        else:
            # 본문이 없고 이미지 설명만 있을 경우 예외 처리
            figcaption = soup.select_one("figure figcaption")
            if figcaption:
                content = figcaption.get_text(strip=True)

        # 본문이 없으면 기본값 설정
        if not content:
            content = "[본문 없음]"

        # 기자명 추출
        author_tags = soup.select("dl.author > a")
        writers = [tag.get_text(strip=True) for tag in author_tags]
        writer = ", ".join(writers) if writers else "알 수 없음"

        return content, writer

    except Exception as e:
        print(f"[본문/기자 크롤링 오류] {url} → {e}")
        return "[본문 없음]", "알 수 없음"

# 전체 수집 및 전송 함수
def main():
    feed = feedparser.parse(RSS_FEED_URL)

    for entry in feed.entries:
        try:
            title = entry.title
            link = entry.link

            # 날짜 정보 처리
            pub_date = entry.get('published_parsed')
            pub_date = datetime(*pub_date[:6]) if pub_date else datetime.now()

            # 카테고리 정보 없으면 기본값 설정
            category = entry.get("category", "기타")

            # 뉴스 본문 및 기자 추출
            content, writer = extract_article_text(link)

            # 전송할 JSON 데이터 구조화
            news_data = {
                "title": title,
                "link": link,
                "write_date": str(pub_date),
                "category": category,
                "content": content,
                "writer": writer
            }

            # Kafka로 데이터 전송
            producer.send(TOPIC, news_data)
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Sent: {title}")

            # 뉴스 전송 간격 조절
            time.sleep(1)

        except Exception as e:
            print(f"[송신 실패] {e}")

# 스크립트 실행 진입점
if __name__ == "__main__":
    main()
```

<br>

📄 \[2\] `consumer_flink.py`
----------------------------

**Kafka 메시지를 실시간 수신하여 전처리하고, DB에 저장하는 Flink 기반 Consumer 코드**  
전체 코드 + 줄별 상세 주석을 제공할게.


```python
# Flink 스트리밍 환경 구성 관련 라이브러리
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream.connectors import FlinkKafkaConsumer

# 시스템, 환경 변수 로딩
import os
import json
from preprocess import (
    transform_extract_keywords, 
    transform_to_embedding, 
    transform_classify_category
)

# PostgreSQL 연결 라이브러리
import psycopg2
from dotenv import load_dotenv

# .env 파일에 있는 환경변수 로딩 (DB, Kafka 설정 포함)
load_dotenv()

# Flink 스트리밍 실행 환경 생성
env = StreamExecutionEnvironment.get_execution_environment()

# Kafka Connector JAR 파일을 Flink 환경에 등록
kafka_connector_path = os.getenv("KAFKA_CONNECTOR_PATH")
env.add_jars(f"file://{kafka_connector_path}")

# Kafka Consumer 속성 설정
kafka_props = {
    'bootstrap.servers': 'localhost:9092',     # Kafka 서버 주소
    'group.id': 'flink_consumer_group'         # Kafka consumer 그룹 ID
}

# Kafka Consumer 객체 생성
consumer = FlinkKafkaConsumer(
    topics='news',                              # 수신할 Kafka 토픽 이름
    deserialization_schema=SimpleStringSchema(),# 문자열 역직렬화 방식
    properties=kafka_props                      # Kafka 연결 속성
)

# Flink 데이터 스트림에 Kafka 소스를 연결
stream = env.add_source(consumer)

# PostgreSQL 저장 함수 정의
def save_to_postgres(article):
    try:
        conn = psycopg2.connect(
            dbname="news",
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
            host="localhost",
            port="5432"
        )
        cur = conn.cursor()

        # INSERT 쿼리 실행 (JSON, 벡터 포함)
        cur.execute(
            """
            INSERT INTO news_article (title, writer, write_date, category, content, url, keywords, embedding)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                article["title"],
                article.get("writer", "알 수 없음"),
                article.get("write_date", "2025-01-01"),
                article["category"],
                article["content"],
                article["link"],
                json.dumps(article["keywords"], ensure_ascii=False),
                article["embedding"]
            )
        )
        conn.commit()
        cur.close()
        conn.close()

        print(f"[저장 완료] {article['title']}")

    except Exception as e:
        print(f"[DB 오류] {e}")

# Kafka 메시지 하나에 대해 처리할 함수 정의
def process_and_save(json_str):
    try:
        data = json.loads(json_str)  # Kafka 메시지를 JSON으로 디코딩

        content = data.get("content", "")
        if not content or content == "[본문 없음]":
            return  # 본문이 없으면 처리하지 않음

        # 전처리: 키워드, 임베딩, 카테고리 추출
        keywords = transform_extract_keywords(content)
        embedding = transform_to_embedding(content)
        category = transform_classify_category(content)

        # 전처리 결과를 원본 데이터에 추가
        data["keywords"] = keywords
        data["embedding"] = embedding
        data["category"] = category

        print(data)  # 콘솔 확인용 출력

        save_to_postgres(data)  # DB 저장

    except Exception as e:
        print(f"[처리 오류] {e}")

# Flink 스트림에서 각 메시지 처리 함수 적용
stream.map(process_and_save)

# Flink Job 실행
env.execute("Flink Kafka Consumer Job")
```

<br>

📄 \[3\] `preprocess.py`
------------------------

**뉴스 본문을 GPT 기반으로 전처리하여 키워드, 임베딩, 카테고리를 생성하는 모듈**  
전체 코드와 줄마다 상세 주석을 정리해줄게.


```python
# OpenAI API 사용을 위한 라이브러리
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()  # .env에 저장된 API 키 로드
```


### 🔹 `preprocess_content()`: 토큰 수 제한 처리

```python
def preprocess_content(content):
    """
    데이터 전처리 - 텍스트 길이 제한 (5000 토큰)
    OpenAI API 호출 시 과도한 토큰 사용 방지를 위한 사전 처리
    """
    import tiktoken  # OpenAI 토큰 계산용 라이브러리

    if not content:
        return ""
    
    # cl100k_base: OpenAI에서 사용되는 기본 인코딩 방식
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(content)

    if len(tokens) > 5000:
        # 토큰이 너무 많을 경우 앞부분만 사용
        truncated_tokens = tokens[:5000]
        return encoding.decode(truncated_tokens)
    
    return content
```


### 🔹 `transform_extract_keywords()`: 키워드 5개 추출

```python
def transform_extract_keywords(text):
    """
    텍스트 데이터 변환 - 키워드 5개 추출
    GPT를 이용하여 뉴스 본문에서 명사 중심 키워드 5개 추출
    """
    text = preprocess_content(text)

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # 최신 소형 고성능 모델
        messages=[
            {"role": "system", "content": "당신은 뉴스 콘텐츠를 분석하여 핵심 키워드 5개를 추출하는 역할을 합니다. 키워드는 명사 중심으로 추출하고, 쉼표로 구분하여 출력해주세요. 예: 경제, 부동산, 금리, 투자, 서울"},
            {"role": "user", "content": text}
        ],
        max_tokens=100  # 출력은 짧기 때문에 적은 토큰으로 제한
    )

    keywords = response.choices[0].message.content.strip()

    # 쉼표 기준으로 분할하고 공백 제거
    return [kw.strip() for kw in keywords.split(',') if kw.strip()]
```


### 🔹 `transform_to_embedding()`: 벡터 임베딩 생성

```python
def transform_to_embedding(text: str) -> list[float]:
    """
    텍스트 데이터 변환 - 벡터 임베딩
    GPT API를 사용하여 본문을 수치형 벡터로 변환 (의미 기반 인코딩)
    """
    text = preprocess_content(text)

    client = OpenAI()
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"  # 소형이지만 의미 기반 성능 우수
    )

    # 벡터 형태로 반환 (리스트[float])
    return response.data[0].embedding
```



### 🔹 `transform_classify_category()`: 뉴스 카테고리 분류

```python
def transform_classify_category(content):
    """
    텍스트 데이터 분류 - 카테고리 분류
    뉴스 본문을 읽고 사전에 정의된 18개 카테고리 중 하나로 분류
    """
    content = preprocess_content(content)

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": """
            다음 뉴스 본문의 주제를 기반으로 가장 알맞은 카테고리를 아래 항목 중 하나로 분류하세요.
            정확히 하나만 선택해서 출력하세요 (텍스트만 출력).
            [IT_과학, 건강, 경제, 교육, 국제, 라이프스타일, 문화, 사건사고, 사회일반, 산업, 스포츠, 여성복지, 여행레저, 연예, 정치, 지역, 취미]
            """},
            {"role": "user", "content": content}
        ],
        max_tokens=10
    )

    model_output = response.choices[0].message.content.strip()

    # 모델이 정해진 카테고리 외의 값을 내놓을 경우 예외 처리
    if model_output not in ["IT_과학", "건강", "경제", "교육", "국제", "라이프스타일", "문화", "사건사고", "사회일반", "산업", "스포츠", "여성복지", "여행레저", "연예", "정치", "지역", "취미"]:
        model_output = "미분류"

    return model_output
```

<br>
<br>

📚 4. 추가 설명 및 실무 팁
==================

🧱 자주 하는 실수 및 주의점
-----------------

### 1\. 🔌 **Kafka 연결 실패**

*   **증상**: `NoBrokersAvailable` 또는 `ConnectionRefusedError`
    
*   **원인**: Kafka 브로커가 실행되지 않았거나 포트가 다름
    
*   **해결 방법**:
    
    *   Kafka 서버(`zookeeper`, `kafka-server`)가 실행 중인지 확인
        
    *   `localhost:9092`가 맞는지 포트 확인
        
    *   방화벽/보안 설정 확인 (특히 WSL2 환경에서는 별도 포트 포워딩 필요할 수 있음)
        


### 2\. 📦 **Kafka Connector JAR 경로 오류 (Flink)**

*   **증상**: `NoClassDefFoundError`, Flink 실행 시 Kafka 소스 인식 실패
    
*   **해결 방법**:
    
    *   `.env`의 `KAFKA_CONNECTOR_PATH` 경로가 실제 JAR 파일의 경로와 일치하는지 확인
        
    *   경로는 절대경로로, `file://` 접두어 포함해야 함 (`file:///home/.../connector.jar`)
        
    *   Flink 버전에 맞는 Kafka Connector JAR 사용 필수 (예: Flink 1.20 → 1.20 전용 JAR 필요)
        


### 3\. 🔐 **OpenAI API Key 오류**

*   **증상**: GPT 관련 함수 실행 시 `401 Unauthorized`
    
*   **해결 방법**:
    
    *   `.env` 파일 내 `OPENAI_API_KEY` 환경변수가 잘못되었거나 누락됨
        
    *   키가 잘 로드되는지 확인: `print(os.getenv("OPENAI_API_KEY"))` 로 점검
        
    *   GPT 요청 시 `max_tokens`를 너무 크게 설정하면 요금 폭탄 주의
        


### 4\. 🧠 **Flink에서 `map()` 함수가 실행되지 않는 경우**

*   **증상**: 아무 작업도 수행되지 않음 (출력/DB 저장 없음)
    
*   **원인**: Flink는 **Lazy Evaluation**을 사용함
    
*   **해결 방법**: `env.execute("Job Name")`가 반드시 있어야 함  
    → 없으면 아무 것도 실행되지 않음
    
<br>

🛠️ 실무 적용 팁
-----------

### 💡 전처리 개선 아이디어

| 항목          | 현재 구현                | 확장 가능성                                             |
| ------------- | ------------------------ | ------------------------------------------------------- |
| 키워드 추출   | GPT 기반 명사 추출       | TF-IDF, YAKE, KeyBERT로 대체 가능                       |
| 임베딩        | `text-embedding-3-small` | `text-embedding-3-large`, SBERT, KoBERT 적용 가능       |
| 카테고리 분류 | 프롬프트 기반 GPT 분류   | 파인튜닝 모델, XGBoost, 로지스틱 회귀 등 모델 적용 가능 |


### 💾 PostgreSQL 활용 팁

*   **임베딩 저장**: 리스트 형태의 float 값을 저장할 경우 → `float8[]` 타입으로도 가능 (단, pgvector가 더 적합)
    
*   **pgvector 사용 추천**:
    
    *   유사도 검색이 필요한 경우 `pgvector` 확장 모듈 도입
        
    *   설치 후: `ALTER TABLE news_article ADD COLUMN embedding vector(1536);`
        
    *   향후 `SELECT * FROM news_article ORDER BY embedding <-> :query_vector LIMIT 5` 가능
        


### 🌐 Kafka 실시간 파이프라인 확장 방안

| 구성 요소      | 확장 제안                                       |
| -------------- | ----------------------------------------------- |
| Kafka Producer | 다양한 RSS 피드 추가 (YTN, 한겨레, 연합뉴스 등) |
| Flink Consumer | 멀티 토픽 소비, 유저 커스텀 필터링 기능 추가    |
| Downstream     | Elasticsearch + Kibana로 시각화 대시보드 구성   |
| 알림 시스템    | Slack, Email 등으로 실시간 요약 전송 가능       |

<br>

🚀 추천 심화 방향
-----------

| 주제                      | 설명                                             |
| ------------------------- | ------------------------------------------------ |
| Apache Beam               | Flink보다 추상화된 스트리밍 처리 API             |
| Debezium + Kafka          | DB 변경 감지 기반 CDC 스트리밍                   |
| LangChain + Vector Search | GPT 연동 Q&A 시스템으로 확장                     |
| Kafka Streams             | Kafka 내장 스트리밍 처리 프레임워크 (Flink 대안) |

<br>

🧾 마무리 요약
---------

이 프로젝트는 단순한 크롤링을 넘어,  
**실시간 데이터 스트리밍, AI 전처리, 벡터 처리, DB 연동**이라는  
복합적인 데이터 파이프라인을 **엔드 투 엔드로 구현한 사례**이다.

실제 서비스에서도 활용 가능한 구조이며,  
단순 데이터 수집이 아닌 **정보의 가치 추출 → 사용자에게 전달**하는  
데이터 제품(Data Product) 관점에서 접근하는 것이 중요하다.

