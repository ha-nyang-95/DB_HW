📄 뉴스 데이터 관리 및 분석 시스템 백엔드 개발 보고서
================================


1\. 서론
------

### 1.1 개발 배경

현대 사회에서는 뉴스 데이터가 실시간으로 생성되고, 그 양은 기하급수적으로 증가하고 있습니다. 사용자는 특정 키워드나 관심 주제에 따라 뉴스를 소비하려는 경향이 강해지고 있으며, 이는 단순한 키워드 검색을 넘어서는 **의미 기반 검색** 및 **개인화 추천**의 필요성을 불러오고 있습니다. 또한, 콘텐츠와의 상호작용(조회수, 좋아요 등)을 통해 사용자 선호도를 분석하고, 이를 기반으로 정보 제공 방식을 개선하는 것도 필수 요소로 떠오르고 있습니다.

이에 따라 본 프로젝트는 뉴스 데이터의 효율적인 저장, 분석, 검색, 추천을 가능하게 하는 **Django 기반 REST API 백엔드 시스템**을 개발하고자 하였습니다. 단순한 데이터 보관을 넘어, **AI 기반 콘텐츠 분석**, **유사 기사 추천**, **사용자 활동 대시보드 제공** 등을 통해 뉴스 소비 경험을 지능적으로 향상시키는 것을 목표로 합니다.

<br>

### 1.2 개발 목표

본 프로젝트는 다음과 같은 기능과 아키텍처적 특징을 구현하고자 하였습니다:

*   **뉴스 데이터의 체계적인 저장 및 관리**: 메타정보, 본문, 키워드, 임베딩 벡터까지 포함한 정형/비정형 정보 통합
    
*   **의미 기반 검색 기능 구현**: pgvector 기반 벡터 유사도 검색을 통한 문맥 기반 기사 추천
    
*   **사용자 상호작용 데이터 분석**: 클릭, 좋아요와 같은 상호작용을 수집하고, 대시보드 형태로 시각화 제공
    
*   **확장 가능한 API 아키텍처 구축**: JWT 인증, 소셜 로그인, CORS 설정 등을 포함한 유연하고 보안성 높은 API 시스템 설계
    

<br>
<br>


2\. 시스템 아키텍처
------------

### 2.1 기술 스택

본 프로젝트는 다음과 같은 기술 스택을 기반으로 설계되었습니다. 각 기술은 역할에 따라 분리되어 있으며, 유지보수성과 확장성을 고려하여 선택되었습니다.

| 범주 | 기술 | 역할 및 목적 |
| --- | --- | --- |
| **백엔드 프레임워크** | Django 5.1.2 | 웹 애플리케이션 서버 및 ORM 기반 데이터 관리 |
| **REST API 개발** | Django REST Framework (DRF) | API 엔드포인트 생성 및 응답 직렬화 |
| **데이터베이스** | PostgreSQL | 관계형 데이터 저장소 및 pgvector 확장 모듈 연동 |
| **벡터 검색** | pgvector | 벡터 기반 유사도 검색 (`embedding <-> vector`) |
| **인증 시스템** | Simple JWT, dj\_rest\_auth, Allauth | JWT 인증 및 소셜 로그인 구현 |
| **프론트엔드 통신** | CORS Headers | 외부 프론트엔드(Vue.js 등)와의 통신 허용 |
| **헬스 체크** | django-health-check | 시스템 상태 모니터링 |
| **캐싱 (옵션)** | Redis (계획 중) | 검색 결과 및 사용자 정보 캐싱을 위한 구조 예정 |
| **응답 템플릿** | 커스텀 Response 클래스 | 일관된 API 응답 메시지 구성 (`SUCCESS_RESPONSE`, `UNAUTHORIZED_RESPONSE`) |

이러한 기술 스택은 뉴스 데이터 저장 및 검색의 **고성능 처리**, **보안성 강화**, **개발 속도 최적화**를 동시에 만족시킬 수 있도록 구성되어 있습니다.

<br>

### 2.2 시스템 구성도

시스템은 크게 4개의 주요 계층으로 구성됩니다:

```mermaid
graph TD
    A["Client (Vue.js)"] -->|REST API| B[Django Backend]
    B --> C["PostgreSQL (pgvector)"]
    B --> D["Authentication Server (JWT)"]
    B --> E["AI Module (OpenAI, LangChain)"]
    B --> F["Dashboard Mocking / Analytics"]
```

*   **Client**: Vue.js 기반의 프론트엔드에서 사용자가 뉴스 검색, 조회, 상호작용을 수행합니다.
    
*   **Backend**: Django 서버는 API 요청을 처리하며, 뉴스 데이터를 PostgreSQL에 저장하고 AI 모듈과 연동하여 키워드 추출, 벡터 유사도 검색 등을 수행합니다.
    
*   **Database**: `pgvector`를 포함한 PostgreSQL은 고차원 임베딩 벡터를 저장하고, 벡터 간 유사도 검색을 지원합니다.
    
*   **Authentication**: Simple JWT와 Allauth를 기반으로, 이메일/비밀번호 인증 및 소셜 로그인까지 처리합니다.
    
*   **AI 연동 및 분석**: LangChain + OpenAI API를 활용하여 콘텐츠 분석 및 추천 로직을 구현합니다.
    

<br>
<br>


3\. 핵심 기능 구현
------------

### 3.1 데이터 모델링

본 프로젝트는 뉴스 데이터를 중심으로 다양한 정보를 저장·분석할 수 있도록 모델을 설계하였습니다. 대표적으로 `NewsArticle` 모델은 **기사 본문**, **카테고리**, **작성자 정보** 외에도, **키워드 배열**, **문장 임베딩 벡터**, **URL**, **작성일** 등을 포함하고 있어 비정형 정보 기반의 추천과 분석이 가능합니다.

```python
class NewsArticle(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.TextField()
    writer = models.TextField()
    write_date = models.DateTimeField()
    category = models.TextField()
    content = models.TextField()
    url = models.TextField(unique=True)
    embedding = ArrayField(models.FloatField())
    keywords = ArrayField(models.TextField())
```

#### 3.1.1 주요 특징

*   **벡터 임베딩을 통한 의미 기반 검색**  
    뉴스 콘텐츠에 대해 사전 학습된 AI 모델을 통해 **문장 임베딩 벡터(ArrayField)** 를 생성하고, `pgvector` 확장을 통해 해당 벡터 간 **거리 기반 유사도 검색**이 가능합니다. 이는 단순 키워드가 아닌 **문맥 유사성** 기반 추천 기능을 가능하게 합니다.
    
*   **키워드 배열을 통한 효율적인 태깅 시스템**  
    `keywords` 필드는 뉴스 본문에서 자동 추출된 주요 키워드를 배열 형태로 저장함으로써, 사용자 대시보드 통계 및 검색 필터링에 활용됩니다.
    
*   **JSON 기반의 상호작용 데이터 저장**  
    `article_interaction` 필드에서는 `{likes: 0, read: 0}` 형식의 데이터를 저장하여, 좋아요나 열람 횟수와 같은 사용자 행동 데이터를 수집 및 분석할 수 있도록 설계되어 있습니다. 이는 **퍼스널라이징 추천**에 활용될 기반 데이터로 기능합니다.
    

<br>

### 3.2 API 엔드포인트 구조

REST API는 Django REST Framework를 기반으로 다음과 같은 주요 기능을 지원합니다.

| 엔드포인트 | 메서드 | 기능 설명 |
| --- | --- | --- |
| `/api/` | GET | 뉴스 목록 조회 (페이징, 카테고리 필터, 정렬 지원) |
| `/api/<id>/` | GET | 특정 뉴스 상세 조회 |
| `/api/<id>/related/` | GET | 같은 카테고리 내 연관 뉴스 조회 |
| `/api/<id>/recommend/` | GET | 임베딩 유사도 기반 추천 뉴스 조회 |
| `/api/dashboard/` | GET | 사용자 선호 통계 기반 대시보드 응답 (목업) |

#### 주요 구현 예시

*   **유사도 검색 쿼리**
    

```sql
SELECT id, title, content, ...
FROM news_article
WHERE id != %s
ORDER BY embedding <-> %s  -- pgvector 유사도 연산자
LIMIT 5
```

*   **시리얼라이저 커스터마이징**
    

```python
class NewsArticleSerializer(serializers.ModelSerializer): 
    embedding = serializers.SerializerMethodField()
    def get_embedding(self, obj):
        if isinstance(obj.embedding, str):
            return json.loads(obj.embedding)
        return obj.embedding
```

*   **대시보드 Mock 데이터**
    

```json
{
  "my_favorite_category": {
    "IT_과학": 0.32, "건강": 0.25, ...
  },
  "my_favorite_key_word": {
    "AI": 15, "블록체인": 10, ...
  }
}
```

<br>
<br>


4\. 기술적 혁신
----------

본 프로젝트는 단순한 CRUD 중심의 뉴스 API 서버를 넘어, **문맥 기반 유사도 추천**, **자동 키워드 추출**, **자연어 기반 사용자 분석** 등 다양한 인공지능 기술을 실용적으로 통합한 것이 특징입니다. 이 장에서는 핵심 기술적 차별점 두 가지인 **벡터 검색 시스템**과 **AI 통합 처리**에 대해 기술합니다.

<br>

### 4.1 벡터 검색 시스템

뉴스 기사 간의 단순 키워드 매칭은 의미 기반 검색의 한계를 지닙니다. 이를 극복하기 위해 본 시스템은 **문장 임베딩을 통한 의미 유사성 기반 검색**을 구현하였습니다.

#### ✅ pgvector 연동

*   **PostgreSQL 확장 모듈**인 `pgvector`를 사용하여, 고차원 벡터를 DB에 저장하고 벡터 간 거리 기반 비교(`embedding <-> vector`)를 가능하게 합니다.
    
*   벡터 유사도 기준 정렬을 통해, 현재 뉴스와 가장 유사한 5개의 기사를 실시간으로 추천합니다.
    

#### ✅ 쿼리 예시

```sql
SELECT id, title, embedding <-> %s AS similarity
FROM news_article
WHERE id != %s
ORDER BY similarity ASC
LIMIT 5;
```

#### ✅ 기술 효과

*   키워드 기반 검색 대비 **문맥 일치율 향상**
    
*   사용자 입력 없이도 유사한 기사 자동 추천 가능
    
*   장기적으로 **퍼스널라이징 추천 모델**과의 연동 가능성 확보
    

<br>

### 4.2 AI 통합

뉴스 본문에 대한 다양한 자연어 처리를 위해 **LangChain**과 **OpenAI API**를 연동하였으며, 이를 통해 **키워드 추출**, **카테고리 자동 분류**, **요약 생성** 등의 기능을 실험적으로 구현하였습니다.

#### ✅ LangChain + OpenAI 활용

*   LangChain 프레임워크를 통해 텍스트 흐름에 기반한 키워드 분리 및 주제 예측 기능 수행
    
*   GPT 기반 API를 사용하여 비정형 뉴스 콘텐츠로부터 정형 정보 구조 생성
    

#### ✅ 자동 키워드 추출 및 분류

*   뉴스 본문을 기반으로 주요 단어를 배열 형태로 추출하여 `keywords` 필드에 저장
    
*   예: `"인공지능"`, `"대선"`, `"환경 정책"` 등 다중 토픽을 인식
    

#### ✅ 향후 확장성

*   감성 분석, 요약문 생성, 사용자 행동 기반 맞춤 추천 모델로 발전 가능
    
*   LangChain Chain 구성 확장 시 **다중 질문 응답형 검색 시스템 구축 가능**
    

<br>
<br>


5\. 성능 최적화
----------

본 시스템은 실시간 검색 및 추천 기능을 포함하고 있어, **빠른 응답성과 높은 동시성 처리**를 요구합니다. 이를 충족하기 위해 데이터베이스 설계와 캐싱 전략 측면에서 다양한 성능 최적화 기법을 적용하거나 계획하였습니다.

<br>

### 5.1 데이터베이스 최적화

#### ✅ 인덱싱 전략

*   `id`, `category`, `write_date`, `url` 등 조회 빈도가 높은 필드에 대해 B-Tree 인덱스를 생성하여 기본 검색 속도 개선
    
*   `url` 필드는 `unique=True`로 지정하여 중복 삽입을 방지하고, 검색 속도 향상을 기대할 수 있음
    

#### ✅ 벡터 검색 특화 인덱스

*   `embedding` 필드에 대해 **pgvector** 전용 인덱스(`IVFFLAT`)를 생성 가능
    
*   고차원 유사도 검색을 위한 벡터 전용 인덱스를 활용하면 수천 건 이상의 벡터 검색에서도 지연 없이 응답 가능
    

```sql
-- 예시: embedding 필드에 대한 벡터 인덱스 생성
CREATE INDEX ON news_article USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);
```

#### ✅ 쿼리 최적화

*   대량의 뉴스 데이터 중 일부만 필터링 또는 정렬하여 가져오기 때문에, 쿼리에는 항상 `LIMIT`, `OFFSET` 또는 Paginator 기반 조회를 사용
    
*   `SELECT` 대상 컬럼을 필요한 범위로 한정하여 I/O 부담 감소
    

<br>

### 5.2 캐싱 전략 (계획 포함)

프로젝트 초기 단계에서는 캐싱이 필수적이지 않았지만, 이후 사용자 수가 증가할 것을 고려하여 다음과 같은 전략을 설계하였습니다.

#### ✅ Redis 기반 캐시 아키텍처 (추후 도입 예정)

*   Django + Redis 연동을 통해 **자주 접근되는 API 응답**(예: 인기 뉴스 목록, 추천 결과 등)을 캐시
    
*   유사한 embedding 결과를 **벡터 키 기반**으로 캐싱하여 DB I/O 최소화
    

#### ✅ 검색 결과 캐싱

*   동일한 검색 조건에 대한 결과는 일정 기간 Redis에 저장하여 응답 속도 향상
    
*   프론트엔드 사용자 입장에서는 **불필요한 재검색 지연 없이** 결과를 확인할 수 있음
    

<br>
<br>


6\. 보안 구현
---------

뉴스 데이터를 관리하는 시스템은 사용자 인증, 데이터 위변조 방지, 접근 권한 제어 등 다양한 보안 요소를 고려해야 합니다. 본 프로젝트는 **JWT 기반 인증 체계**, **소셜 로그인**, **입력값 검증** 등 다층적인 보안 장치를 마련하여 안정적인 API 서비스를 제공할 수 있도록 설계되었습니다.

<br>

### 6.1 인증 시스템

#### ✅ JWT 기반 인증

본 시스템은 `Simple JWT`를 사용하여 사용자 인증을 처리합니다. 사용자가 로그인 시 발급받는 **Access Token**은 1일간 유효하며, **Refresh Token**은 5일 동안 사용 가능합니다. 토큰은 HTTP 요청의 `Authorization: Bearer <token>` 헤더에 포함되어 인증에 사용됩니다.

```python
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=5),
    ...
}
```

#### ✅ 회원가입 및 로그인 API

*   `/api/accounts/signup/`: 이메일, 사용자명, 비밀번호를 입력받아 회원가입을 처리합니다.
    
*   `/api/accounts/login/`: 유효한 이메일/비밀번호 입력 시 JWT 토큰 쌍을 반환합니다.
    
*   `/api/accounts/token/refresh/`: 만료된 Access Token을 Refresh Token으로 재발급합니다.
    
*   `/api/accounts/me/`: 로그인된 사용자의 정보를 조회할 수 있는 인증 보호 API입니다.
    

```http
GET /api/accounts/me/
Authorization: Bearer <access_token>
```

#### ✅ 소셜 로그인 통합

`django-allauth` 기반의 백엔드 인증 구조를 적용해 소셜 로그인 기능 통합이 가능하도록 설정하였습니다. 현재는 이메일 기반 인증을 기본으로 하며, 향후 Google, Kakao 등 외부 인증 연동도 손쉽게 확장 가능합니다.

```python
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]
```

<br>

### 6.2 데이터 보안

#### ✅ 입력값 검증

*   `SignupSerializer`에서 `password` 필드를 `write_only`로 설정하여, 응답 메시지를 통한 유출을 원천적으로 차단합니다.
    
*   비밀번호는 `create_user()` 호출 시 Django 내부의 암호화 로직을 거쳐 저장되므로 평문 노출 위험이 없습니다.
    

```python
extra_kwargs = {'password': {'write_only': True}}
```

#### ✅ SQL Injection 방지

*   Django ORM을 기반으로 쿼리를 생성하기 때문에 SQL Injection 취약점을 방지할 수 있으며, 직접 커넥션 커서를 사용할 경우에도 파라미터 바인딩을 통해 보안을 유지합니다.
    

```python
cursor.execute("SELECT ... WHERE id = %s", [safe_input])
```

#### ✅ XSS 및 CSRF 방어

*   기본적으로 Django의 템플릿 시스템은 XSS 필터링을 수행하며, REST API에서는 상태 기반 요청이 아닌 토큰 기반 인증을 통해 CSRF 방지 구조를 갖추고 있습니다.
    
*   또한 `CORS_ALLOW_CREDENTIALS = True` 설정과 함께, 정확한 `CORS_ALLOWED_ORIGINS`를 지정하여 신뢰할 수 있는 출처만 통신을 허용합니다.
    

<br>
<br>


7\. 테스트 및 코드 품질 관리
------------------

지속 가능한 백엔드 시스템을 운영하기 위해서는 기능 구현뿐만 아니라, **테스트 자동화**, **일관된 코드 스타일**, **타입 안정성 확보**가 필수적입니다. 본 프로젝트는 초기 MVP 단계에서도 품질 유지를 위한 기본적인 관리 체계를 갖추고 있으며, 확장에 대비한 구조를 마련해두었습니다.

<br>

### 7.1 테스트 전략

#### ✅ 단위 테스트 (Unit Test)

*   각 기능별 뷰(View) 및 직렬화(Serializer) 단위로 테스트 코드를 작성할 수 있도록 `tests.py` 파일을 각 앱에 포함시켰습니다.
    
*   예: 회원가입 API는 유효한 입력값에 대해 성공 응답을 반환하고, 중복 이메일 혹은 유효하지 않은 포맷에 대해서는 적절한 에러 메시지를 반환하는지 검증합니다.
    

```python
def test_signup_valid(self):
    response = self.client.post('/api/accounts/signup/', {
        'email': 'test@example.com',
        'username': 'tester',
        'password': 'securepass'
    })
    self.assertEqual(response.status_code, 201)
```

#### ✅ 통합 테스트 (Integration Test)

*   JWT 기반 인증 흐름에 대한 전반적인 검증을 포함합니다.
    
    *   회원가입 → 로그인 → 토큰 발급 → 보호된 API 접근
        
*   인증 토큰이 만료된 경우 적절히 갱신되며, 권한 없는 접근은 차단되는지 확인합니다.
    

#### ✅ API 엔드포인트 테스트

*   `/api/<id>/recommend/`, `/api/<id>/related/` 등에서 벡터 유사도 기반 추천이 정상적으로 작동하는지 확인합니다.
    
*   Django의 `APITestCase` 및 `APIClient`를 활용하여 실제 API 사용 흐름과 유사한 테스트 환경을 제공합니다.
    

<br>

### 7.2 코드 품질 관리

#### ✅ 코드 스타일 정리: `Black`

*   Python 코드 포맷터 **Black**을 사용하여 모든 코드의 스타일을 자동 정렬하였습니다. 이를 통해 팀 간 협업 시 코드 해석 일관성을 높일 수 있습니다.
    
*   예를 들어, `views.py`, `serializers.py` 등 모든 주요 파일은 Black으로 포맷팅 후 커밋합니다.
    

#### ✅ 커밋 전 검사: `pre-commit` 훅

*   `.pre-commit-config.yaml` 설정을 통해 Git 커밋 시 자동으로 스타일 체크, 중복 import 제거, 포맷 오류 수정이 이루어지도록 구성하였습니다.
    
*   이를 통해 스타일 규칙 위반 코드가 배포되는 것을 사전 차단합니다.
    

#### ✅ 타입 힌팅 및 정적 분석

*   주요 함수에 대해 Python 3의 **타입 힌팅(type hinting)** 을 적극적으로 활용하였습니다.
    
*   이는 코드의 안정성과 가독성을 높이고, Pyright 또는 mypy와 같은 정적 분석 도구를 통해 조기 오류 탐지가 가능합니다.
    

```python
def get_embedding(self, obj: NewsArticle) -> list[float]:
    ...
```

<br>
<br>


8\. 결론 및 향후 계획
--------------

### 8.1 성과

본 프로젝트는 **뉴스 데이터의 수집, 분석, 검색, 추천**이라는 복합적인 기능 요구사항을 안정적으로 충족하는 백엔드 시스템을 성공적으로 구축하였습니다. 주요 성과는 다음과 같습니다.

*   **의미 기반 검색 기능 구현**  
    뉴스 본문에 대해 벡터 임베딩을 생성하고, pgvector 기반의 유사도 검색을 통해 키워드 일치가 아닌 **문맥 유사성 기반 추천 시스템**을 완성하였습니다.
    
*   **확장 가능한 RESTful API 구조 설계**  
    Django REST Framework 기반의 API 구조는 모듈화되어 있으며, JWT 인증과 소셜 로그인 기능이 통합되어 있어 보안과 사용자 편의성을 모두 확보하였습니다.
    
*   **사용자 상호작용 데이터 분석 구조화**  
    좋아요 및 조회수 등의 행동 데이터를 JSON 구조로 저장하고, 이를 활용해 향후 **사용자 선호 기반 대시보드 및 개인화 기능**으로 확장할 수 있는 기반을 마련하였습니다.
    
*   **테스트 및 코드 품질 관리**  
    Black 기반 포맷팅, pre-commit 훅, 타입 힌팅 도입을 통해 코드 품질을 유지하며, 기능별 테스트 작성으로 안정성을 확보하였습니다.
    

<br>

### 8.2 향후 개선 사항

본 프로젝트는 MVP 수준의 서비스 구현에 집중하였으며, 다음과 같은 측면에서 고도화가 가능합니다:

*   **실시간 데이터 처리 파이프라인 구축**  
    현재는 정적 데이터 중심이나, 향후 Kafka-Flink 등의 기술을 활용해 실시간 뉴스 수집 및 스트리밍 분석 기능을 도입할 수 있습니다.
    
*   **머신러닝 기반 추천 시스템 고도화**  
    사용자의 상호작용 로그, 키워드 선호도 등을 바탕으로 개인화 추천 모델을 개발하고, 실시간으로 사용자 행동에 반응하는 시스템을 구현할 수 있습니다.
    
*   **마이크로서비스 아키텍처 전환 검토**  
    인증, 뉴스 분석, 추천 기능 등을 서비스 단위로 분리하여 **서비스 간 독립성과 유지보수 효율성**을 향상시키는 방향으로 아키텍처를 발전시킬 수 있습니다.
    
*   **OpenAI 연동 확장**  
    현재는 키워드 추출 위주로 사용하였으나, 향후 뉴스 요약, 감정 분석, 질문응답 등으로 확장 가능성이 큽니다.
    