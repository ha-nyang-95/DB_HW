# Elasticsearch 설치 및 기본 개념
## Elasticsearch 개요
대량의 데이터를 빠르고 효율적으로 검색하고 분석할 수 있게 만들어진 분산구조 검색엔진
### 정보 검색이란?
- 대규모 데이터 속에서 사용자가 원하는 정보를 찾아 제공하는 기술
- 웹 문서, 이미지, 동영상, 연구 논문 등 다양한 데이터 유형을 대상으로 함
- Google, Microsoft 등 글로벌 기업에서 핵심적으로 활용
- 검색 시스템에서의 요구사항
### 정보 검색의 핵심 기술
- 데이터 수집(Data Collection)
- 데이터 저장(Data Storage) - 역색인(Inverted Index)
- 검색 알고리즘(Search Algorithm)
### 기존 RDB 검색
- '블루투스 이어폰'이라는 타이틀을 가진 상품 검색한다는 가정
- 문제점
  - 쿼리가 복잡해짐
  - 성능에 문제 발생
  - 스펠링 오류, 유사 검색 불가
### 검색 엔진의 순위와 종류
### Elasticsearch
- Elasticsearch는 강력한 오픈소스 검색 및 분석 엔진
- 수평적 확장성, 안정성, 쉬운 관리를 위한 설계
- Apache Lucene 기반이며, Elastic Stack의 일부로 Elastic Stack은 Logstash(로그 수집), Beats, Kibana(시각화)를 포함
### Elasticsearch와 Lucene의 관계
- Elasticsearch
  - 분산 검색 엔진, 데이터를 저장하고 빠르게 검색
  - Lucene을 내부 엔진으로 사용
- Lucene
- Elasticsearch vs Lucene: Elasticsearch는 Lucene을 기반으로 동작하며 REST API 및 분산 환경 지원
### Lucene
- 문서가 들어오고 분석하고 세그먼트에 저장하고 세그먼트 읽음, 관련성 높은 결과를 찾아옴
### Lucene이란?
- 검색용 서비스의 핵심: Lucene
  - Elasticsearch에서의 검색관련 API의 대부분은 루씬 기반의 검색 API에서 출발
  - 분산 처리, 캐싱, 샤드 기반 검색 등의 추가 기능을 제공하여 대규모 데이터 검색을 최적화
  - 결국, Elsticsearch는 Lucene을 여러개로 쪼개서 분산 저장
### Lucene의 segment
- 세그먼트란?
  - Lucene에서 색인된 문서들을 저장하는 최소 단위
- 세그먼트의 장점
  - 동시성 확보
  - 빠른 색인 처리
  - 안정적인 검색
### Elasticsearch
- Data Collection(beats) -> Buffering(Kafka) -> Data Aggregation & Processing(logstash) -> Indexing & Storage(elasticsearch) -> Analysis & Visualization(Kibana)
### Elasticsearch 특징
- 분산 구조
- 전문 검색
- 확장성
- 유연성
### Elasticsearch 활용
- 기업 검색
- 로그 수집 및 분석
- 보안 정보 및 이벤트 관리
- 데이터 분석
- 개인화 및 추천 시스템
### Elasticsearch 기본 요소
- 문서
  - 색인될 수 있는 기본 정보 단위
  - JSON 형식으로 표현
- 필드
  - 가장 작은 데이터 단위
  - 키-값 쌍을 의미
### Elasticsearch 데이터 저장 및 관리
- 인덱싱
  - 각 인데스는 Databasr처럼 동작
- 샤딩
  - 인덱스는 여러 개의 샤드로 나눌 수 있음
- 레플리카
### Elasticsearch 검색 동작 원리
- 질의 처리
- 연관성 점수 계산
  - TF-IDF 및 BM25 등의 알고리즘을 사용하여 각 문서가 사용자의 질의와 부합하는지 계산
- 준실시간 검색(NRT)
  - Elasticsearch는 데이터를 검색하면서 동시에 색인할 수 있는 준실시간 검색 기능을 제공
- 준실시간 검색이 가능한 이유
  - 메모리 기반 버퍼링으로 색인 속도 향상
  - 비동기 색인 처리로 검색과 색인을 동시에 수행
  - Lucene 엔진 최적화를 통한 빠른 색인 적용
- 그 밖의 Elasticsearch 특징
  - 유연한 JSON 데이터 관리
    - 필드를 문서마다 다르게 넣을 수 있다.
  - 정밀한 검색 및 필터링
  - 다양한 검색 쿼리 지원
  - 다양한 클라이언트 지원
  - 확장성과 안정성
  - Kibana 데이터 시각화 

## Elasticsearch 설치 및 환경 구성
### Docker를 통한 설치
- os 환경에 영향받지 않도록 docker를 통한 설치를 권장
### Elasticsearch 환경 구성
- docker compose -f docker-compose-elastic.yml up -d
  - docker-compose.yml 명이 다를 때는 이와 같이 -f 옵션을 통해 명령어로 띄울 수 있음
  - Image
    - 사용할 Docker 이미지를 지정
  - cluster.name
    - 컨테이너 이름을 지정
  - node.name
  - cluster.name
  - discovery.seed hosts
    - 노드 여러개가 서로 인식할 수 있도록 사용
  - cluster.initial_master_nodes
  - node.roles
    - 이 노드의 역할을 설정
  - jvm.options
    - Elasticsearch가 사용할 Java 힙 메모리 크기를 지정
  - volumes
  - ports
  - networks
    - Docker로 띄운 컨테이너간 통신

## Elasticsearch REST API & Document CRUD
### Elasticsearch의 데이터 교환
- 방식
- REST API의 특징
### Elasticsearch의 RESTful API
- RESTful API
### Elasticsearch의 index 생성
- Index를 Elasticsearch가 자동 매핑으로 필드 타입을 추론해서 설정
- 인덱스를 미리 정의된 설정으로 명시적으로 생성(mapping도 가능)
### Document CRUD
- POST를 활용한 문서 생성
- GET을 활용한 문서 조회
- POST를 통한 업데이트
  - 기존 내용을 변경
  - 새로운 필드 추가
- DELETE를 통한 삭제
  - 실제로 삭제되는 것이 아니고 표시되기 때문에 flush를 해야 완전 삭제  
- Upsert
  - 업데이트와 삽입을 결합한 연산
    - 해당 ID의 문서가 존재 -> 업데이트 수행
    - 존재 x -> 수행 x
### Elasticsearch 문서 업데이트
- Elasticsearch의 문서는 불변하므로 직접 수정되지 않으며, 업데이트 시 새로운 문서로 저장 등으로 사용 가능
- 업데이트 과정
  - 기존 문서 조회
  - 변경 사항 적용
  - 새 문서 색인
  - 이전 문서 삭제 처리
  - 세그먼트 병합
### Elasticsearch에서 세그먼트와 Flush의 관계
- upsert & update는 기존 문서를 수정하는 것이 아니라 새로운 세그먼트를 생성하는 방식으로 동작
- Flush는 새로운 세그먼트를 디스크에 기록하는 과정
- 세그먼트가 증가하면 자동으로 병합 수행