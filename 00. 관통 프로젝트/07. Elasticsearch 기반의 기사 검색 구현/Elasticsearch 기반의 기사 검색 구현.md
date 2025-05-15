# Elasticsearch 기반의 기사 검색 구현
## 관통 프로젝트 안내
### 프로젝트 개요
- Elasticsearch를 이용하여 PostgreSQL에 저장된 기사를 검색하고, 검색된 결과를 대시보드로 시각화하는 것이 최종 목표입니다.
- Django REST Framework(DRF)를 통해 검색 API를 제공하고, Vue.js에서 검색 UI를 구현하여 사용자 편의성을 높입니다.
- 실시간 혹은 일정 주기로 기사 데이터를 동기화하고, 빠르고 정확한 검색 환경을 제공합니다.
- 또한, Kibana를 활용하여 주요 지표(검색 트렌드, 기사 카테고리 분포 등)를 시각적으로 확인할 수 있는 대시보드를 제작할 수 있습니다.
### 목표
- Elasticsearch와 PostgreSQL을 연동하며 데이터에 대한 검색 기능을 구축할 수 있다.
- Django REST Framework(DRF)로 검색 API를 설계 및 구현할 수 있다.
- Vue.js로 웹 검색 UI를 구성하고, 사용자 인터페이스를 직관적으로 설계할 수 있다.
- Kibana 대시보드를 활용하여 다양한 관점에서 데이터 시각화와 모니터링을 수행할 수 있다.
### 준비사항
#### 사용 데이터
- PostgreSQL에 저장된 뉴스 기사 데이터(기사 제목, 작성자, 작성일, 내용, URL, 키워드 등)
- Elasticsearch 색인(index)으로 사용될 전처리 과정의 데이터
#### 개발언어/프로그램
- Python(Django REST Framework, Airflow DAG, 데이터 동기화 스크립트 등)
- Vue.js(검색 UI 구현)
- Elasticsearch & Kibana(검색 엔진 및 시각화 대시보드)
- PostgreSQL(뉴스 기사 저장 및 관리)
- Docker(개발 환경 및 배포 환경 구성 시 활용)
### 구현 방법
#### 1) Elasticsearch 세팅
- Elasticsearch 설치 및 구성(Docker Compose 또는 직접 설치)
- 뉴스 기사 데이터를 저장할 인덱스(news) 생성
- 검색 성능 및 매핑 설정(분석기, 토크나이저 설정 등)
#### 2) DRF 검색 기능 추가
- Django REST Framework로 검색 API 엔드포인트 구현(GET/news/search/)
- 요청 파라미터를 받아 Elasticsearch에서 기사 검색
- 검색 결과를 JSON 형태로 반환
#### 3) Vue.js 검색 UI 추가
- Vue.js 프로젝트 생성 후, 검색 창과 결과 목록 UI 개발
- DRF API 연동하여 사용자 검색 요청 처리
- 결과 목록 정렬, 필터 등 추가 기능 고려
#### 4) DB-Elasticsearch 동기화
- PostgreSQL과 Elasticsearch 간의 데이터 동기화 수행
  - RDB에 저장함과 동시에 별도로 Elasticsearch에 따로 적재(트랜잭션이 성공한 경우만 Elasticsearch로 보냄)
  - 배치로 동기화 - Airflow나 logstash 기반으로 Cronjob 형태로 RDB에서 수정된 데이터를 읽어서 Elasticsearch에 일괄 동기화(postgresql에 추가적인 컬럼 필요 - update 시간)
#### 5) Kibana 시각화 대시보드
- Kibana에 Elasticsearch 인덱스를 연결
- 기사 카테고리, 키워드, 작성일 등을 기반으로 한 다양한 시각화 차트(파이 차트, 바 차트, 라인 차트 등) 구성
- 실시간 분석 모니터링 페이지 구성
### 관통 프로젝트 가이드
#### 데이터 저장(기사 DB 구축)
- RSS를 활용하여 기사 데이터를 테이블 단위로 저장하고 관리
#### Elasticsearch 색인
- Kafka Consumer에서 데이터를 DB에 저장하는 동시에 Elasticsearch 인덱스도 함께 갱신
#### 검색 및 UI
- DRF를 통해 검색 API를 구현하고, Vue.js로 검색 화면을 구성해 사용자 편의성 제공
#### 시각화
- Kibana를 통해 검색 트렌드, 인기 기사, 카테고리 분포 등을 대시보드로 시각화
#### 데이터 동기화
- RDB에 저장함과 동시에 별도로 Elasticsearch에 따로 적재(트랜잭션이 성공한 경우만 Elasticsearch로 보냄)
- 배치로 동기화 - Airflow나 logstash 기반으로 Cronjob 형태로 RDB에서 수정된 데이터를 읽어서 Elasticsearch에 일괄 동기화(postgresql에 추가적인 컬럼 필요 - update 시간)
### 요구사항
#### Elasticsearch 세팅 후 PostgreSQL과 연동하여 검색 서비스를 구축
#### 기본 기능
- 데이터 검색 및 시각화
  - Elasticsearch 인덱스 생성 및 매핑 설정
  - PostgreSQL DB에 저장된 기사 데이터 색인
  - DRF API를 통해 검색 기능 구현(키워드, 날짜, 카테고리 등)
#### 요청 조건
- RDB에 저장함과 동시에 별도로 Elasticsearch에 따로 적재(트랜잭션이 성공한 경우만 Elasticsearch로 보냄)
- 배치로 동기화 - Airflow나 logstash 기반으로 Cronjob 형태로 RDB에서 수정된 데이터를 읽어서 Elasticsearch에 일괄 동기화(postgresql에 추가적인 컬럼 필요 - update 시간)
- 뉴스 기사 검색 UI를 Vue.js로 구현
#### 결과
- DB와 Elasticsearch가 연동된 색인 및 검색 기능 시연 가능
- Vue.js 검색 화면에서 제목 검색 및 결과 리스트 확인 가능
### 추가기능(선택사항)
#### Kibana 고급 분석 또는 추가 UI 확장(예: 연관 키워드 추천, 자동완성 기능 등)
#### 요청 조건
- 기사 내 키워드를 기반으로 자동완성 기능 추가
- 검색 결과에 기반한 연관 키워드 추천 API(Elasticsearch의 ngram 분석기, suggest 기능 등 활용)
- Kibana로 인덱스 연결 및 간단한 대시보드 작성
- Kibana 대시보드를 통한 기본 시각화 및 연관 키워드 관계(네트워크 그래프 등)를 시각화
#### 결과
- 사용자 입력에 따른 실시간 자동완성 기능 제공
- 검색 결과를 Kibana에서 차트(바 차트, 파이 차트 등)로 확인 가능
- Kibana를 통한 시각화 및 연관 키워드 그래프 등 시각화 기능 제공을 통해 분석 범위 확대