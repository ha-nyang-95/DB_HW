# 📘 데이터 분석 & 엔지니어링 정리 (DB_HW)

> 본 저장소는 데이터 분석, SQL, 머신러닝, 데이터 엔지니어링 및 스트리밍 프로젝트를 체계적으로 정리한 자료입니다. 실습 중심의 폴더 구성과 학습 흐름에 맞춘 목차로 구성되어 있으며, 각 주제는 실습과 이론이 병행됩니다.

---

## 📚 목차

### 📁 00. 관통 프로젝트

| 순번 | 주제                                                                                   | 설명                                            |
| ---- | -------------------------------------------------------------------------------------- | ----------------------------------------------- |
| 01   | [데이터 분석 시각화](./00.%20관통%20프로젝트/01.%20데이터%20분석%20시각화)             | 실제 데이터를 시각적으로 분석하여 인사이트 도출 |
| 02   | [스트리밍 파이프라인 구축](./00.%20관통%20프로젝트/02.%20스트리밍%20파이프라인%20구축) | Kafka-Flink를 활용한 실시간 데이터 흐름 구성    |

---

### 📁 01. SQL

| 순번 | 주제                                         | 설명                                    |
| ---- | -------------------------------------------- | --------------------------------------- |
| 01   | [RDBMS 기초](./01.%20SQL/01.%20RDBMS)        | 관계형 데이터베이스 구조와 설계 개념    |
| 02   | [SQL 기초 문법](./01.%20SQL/02.%20Basic_SQL) | SELECT, JOIN, WHERE 등 기본 질의문      |
| 03   | [고급 SQL](./01.%20SQL/03.%20SQL_Advanced)   | 윈도우 함수, 서브쿼리, 인덱스 최적화 등 |

---

### 📁 02. 데이터 분석 및 머신러닝

| 순번 | 주제                                                                                       | 설명                                     |
| ---- | ------------------------------------------------------------------------------------------ | ---------------------------------------- |
| 01   | [Pandas 기초](./02.%20데이터%20분석%20및%20머신러닝/01.%20Pandas%20기초)                   | 시리즈, 데이터프레임 생성 및 연산        |
| 02   | [Pandas 심화](./02.%20데이터%20분석%20및%20머신러닝/02.%20Pandas%20심화)                   | 그룹화, 병합, 결측치 처리 등 실전 활용   |
| 03   | [통계 기초](./02.%20데이터%20분석%20및%20머신러닝/03.%20통계%20기초)                       | 평균, 분산, 정규분포 등 통계 기본 개념   |
| 04   | [데이터 시각화](./02.%20데이터%20분석%20및%20머신러닝/04.%20데이터%20시각화)               | matplotlib, seaborn을 활용한 시각화 실습 |
| 05   | [EDA](./02.%20데이터%20분석%20및%20머신러닝/05.%20EDA)                                     | 데이터 탐색, 이상치 분석, 기초 시각화    |
| 06   | [데이터 수집](./02.%20데이터%20분석%20및%20머신러닝/06.%20데이터%20수집)                   | 크롤링, API, 엑셀/CSV/DB 연결 등         |
| 07   | [머신러닝 개요](./02.%20데이터%20분석%20및%20머신러닝/07.%20머신러닝%20개요)               | 지도/비지도 학습 개념 및 용어            |
| 08   | [머신러닝 알고리즘 1](./02.%20데이터%20분석%20및%20머신러닝/08.%20머신러닝%20알고리즘%201) | 선형회귀, 로지스틱회귀, KNN 등           |
| 09   | [머신러닝 알고리즘 2](./02.%20데이터%20분석%20및%20머신러닝/09.%20머신러닝%20알고리즘%202) | 앙상블, SVM, 클러스터링 등               |
| 10   | [기초 수학](./02.%20데이터%20분석%20및%20머신러닝/10.%20데이터분석을%20위한%20기초수학)    | 벡터, 행렬, 지수로그 등 데이터 분석 수학 |
| 11   | [통계 기법](./02.%20데이터%20분석%20및%20머신러닝/11.%20데이터분석_통계기법)               | 카이제곱, T검정, ANOVA 등 통계 분석 방법 |

---

### 📁 03. 데이터 사이언스 (Kafka / Flink)

| 순번 | 주제                                                                        | 설명                                     |
| ---- | --------------------------------------------------------------------------- | ---------------------------------------- |
| 02   | [Kafka 기본 구조](./03.%20데이터%20사이언스/02.%20Kafka%20기본%20구조)      | 브로커, 토픽, 파티션 구조 개념 이해      |
| 03   | [프로듀서 & 컨슈머](./03.%20데이터%20사이언스/03.%20프로듀서%20&%20컨슈머)  | Kafka에서 메시지 송수신 흐름 실습        |
| 04   | [모니터링](./03.%20데이터%20사이언스/04.%20모니터링)                        | Prometheus + Grafana 기반 Kafka 모니터링 |
| 06   | [Flink 설치 및 구조](./03.%20데이터%20사이언스/06.%20Flink%20설치와%20구조) | Flink 아키텍처 및 로컬 설치 실습         |
| 07   | [Flink DataStream](./03.%20데이터%20사이언스/07.%20DataStream)              | Flink 실시간 처리 API 실습               |
| 08   | [Checkpointing](./03.%20데이터%20사이언스/08.%20Checkpointing)              | 장애 복구를 위한 Flink 상태 저장 실습    |

---

### 📁 04. 데이터 엔지니어링

| 순번 | 주제                                                                                | 설명                                                                  |
| ---- | ----------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| 01   | [Spark 설치와 구조](./04.%20데이터%20엔지니어링/01.%20Spark%20설치와%20기본%20구조) | Spark 실행 환경 구성 및 실행 흐름 이해                                |
| 02   | [RDD](./04.%20데이터%20엔지니어링/02.%20RDD)                                        | 대규모 데이터 처리의 효율성과 신뢰성을 보장하는 분산 데이터 구조 이해 |
---

## 🛠️ 사용 기술 스택 정리

> 본 학습 및 실습을 통해 익힌 기술 스택입니다.

### 📊 분석 및 시각화
- **Python** (3.10)
- **Pandas**, **NumPy**
- **Matplotlib**, **Seaborn**
- **Scikit-learn** (기초 머신러닝)

### 🧠 통계 및 수학
- 기술 통계, 확률분포
- T-test, ANOVA, 카이제곱
- 벡터/행렬 연산, 지수로그

### 💾 데이터 수집 및 처리
- 웹 크롤링 (requests, BeautifulSoup)
- Excel/CSV/JSON/DB 입력
- API 활용

### 🧮 SQL 및 RDBMS
- PostgreSQL, MySQL
- SQL 기본/고급 문법
- 서브쿼리, 윈도우 함수, 인덱스 튜닝

### 🚀 데이터 엔지니어링
- Apache Spark (설치 및 기본 실행, RDD/DF 연산)
- Kafka (토픽, 프로듀서, 컨슈머)
- Apache Flink (DataStream, Checkpoint)
- Docker, WSL2 + Ubuntu 환경 구성

### 📈 실시간 스트리밍 및 모니터링
- Kafka → Flink 연동 파이프라인
- Prometheus + Grafana 모니터링 시스템 구성

