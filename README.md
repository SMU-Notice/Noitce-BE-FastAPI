# SMU Notice

FastAPI 기반 게시판 스크래핑 시스템으로, 대학교 공지사항을 자동으로 수집하고 관리하는 레포입니다.

## 📑 목차

1. [프로젝트 소개](#1-프로젝트-소개)
   - [1.1 프로젝트 개요](#11-프로젝트-개요)
   - [1.2 전체 시스템 개요](#12-전체-시스템-개요)
   - [1.3 해당 서버 역할](#13-서버-역할-및-기능)
2. [서버 아키텍처](#2-서버-아키텍처)
3. [기술 스택](#3-기술-스택)
4. [스크래퍼 추가 방법](#4-스크래퍼-추가-방법)
   - [4.1 게시판(Board) 스크래퍼 추가 방법](<#41-게시판(Board)-스크래퍼-추가-방법>)
   - [4.2 게시물(Post) 스크래퍼 추가 방법](<#42-게시물(Post)-스크래퍼-추가-방법>)
5. [개발 가이드라인](#5-개발-가이드라인)
6. [시작하기](#6-시작하기)
7. [API 엔드포인트](#7-api-엔드포인트)

## 1. 프로젝트 소개

### 1.1 프로젝트 개요

- **목적**: 대학교 게시판의 공지사항들을 자동으로 수집하여 통합 관리 및 새로운 게시물 이메일 전송

### 1.2 전체 시스템 개요

- **스크랩핑 서버** : 게시판 데이터 수집 및 저장
- ** API 서버** : 회원 관리, 웹 API 서비스, 이메일 전송

![image]()

### 1.3 서버 역할 및 기능

#### 역할

- 게시물 데이터 수집 및 저장
- 게시물 본문 및 사진 요약
- 새로운 게시물 정보 API 서버로 전송

#### 기능

- **자동 스크래핑**: 비동기 스케줄러 기반 주기적 수집
- **중복 검사**: 기존 게시물과 신규 게시물을 구분하여 처리
- **데이터 저장**: SQLAlchemy ORM을 통한 체계적 저장
- **확장성**: 새로운 게시판 추가가 간편한 모듈형 구조
- **AI 요약**: AI API 연동으로 자동 요약 생성

## 2. 서버 아키텍처

### DDD(Domain-Driven Design) 계층 구조

![image](https://github.com/user-attachments/assets/accdd58e-8537-4fd4-a0c7-ed61a2a1df98)

```
app/
├── main.py                     # FastAPI 엔트리포인트
├── config/                     # 설정 관리
└── board/
    ├── domain/                 # 🟢 도메인 계층
    │   └── repository/        # Repository 인터페이스
    ├── application/           # 🟡 애플리케이션 계층
    │   ├── services/
        └── handlers/          # 유스케이스 처리
    └── infra/                 # 🔴 인프라 계층
        ├── repository/        # Repository 구현체
        ├── scraper/          # 스크래퍼 관련
        ├── schedulers/       # 스케줄링 관리
        └── db_models/        # SQLAlchemy 모델
```

### 계층별 책임

#### 🟢 Domain Layer (도메인 계층)

- **Post 엔티티**: 게시물의 핵심 비즈니스 규칙과 로직
- **Repository 인터페이스**: 데이터 저장소에 대한 추상화
- **순수한 비즈니스 로직**: 외부 의존성 없는 도메인 지식

#### 🟡 Application Layer (애플리케이션 계층)

- **Handler**: 유스케이스 조율 및 비즈니스 플로우 관리
- **서비스 조합**: 여러 도메인 서비스 간의 협력 관리
- **트랜잭션 처리**: 데이터 일관성 보장

#### 🔴 Infrastructure Layer (인프라 계층)

- **Repository 구현체**: 실제 데이터베이스 접근 로직
- **Scraper**: 외부 웹사이트에서 데이터 수집
- **Scheduler**: 주기적 작업 스케줄링
- **DB Models**: SQLAlchemy ORM 모델

### 데이터 흐름

```
1. 스케줄러 → 스크래퍼 실행
2. 스크래퍼 → 웹사이트에서 데이터 수집
3. 핸들러 → 신규/기존 게시물 분류
4. Repository → 데이터베이스 저장/업데이트
4. Sender -> 새로운 게시물 정보 API 서버로 전송
```

## 3. 기술 스택

### Framework

- **FastAPI**: 고성능 비동기 웹 프레임워크
- **Python 3.11**: 주 개발 언어

### 아키텍처 & 의존성 관리

- **dependency-injector**: 의존성 주입 컨테이너
- **Clean Architecture**: DDD 기반 계층형 아키텍처

### 데이터베이스 & ORM

- **MySQL**: 메인 데이터베이스
- **SQLAlchemy**: ORM 및 데이터베이스 연동
- **aiomysql**: 비동기 MySQL 드라이버

### 스크래핑 & 파싱

- **aiohttp**: 비동기 HTTP 클라이언트
- **BeautifulSoup4**: HTML 파싱
- **requests**: HTTP 요청 처리

### 스케줄링 & 백그라운드

- **AsyncIOScheduler**: 주기적 작업 스케줄링

### AI & 자연어 처리

- **OpenAI API**: 텍스트 요약 생성
- **Naver OCR**: 이미지 텍스트 추출

### 개발 & 배포

- **Docker**: 컨테이너화
- **Docker Compose**: 멀티 컨테이너 관리
- **logging**: 로깅 시스템

### 환경 설정

- **python-dotenv**: 환경변수 관리

### 의존성 관리

- **pip**: 패키지 관리
- **requirements.txt**: 의존성 명시

## 4. 스크래퍼 추가 방법

새로운 게시판의 스크래퍼를 추가하는 과정을 단계별로 설명합니다.

### 4.1 게시판(Board) 스크래퍼 추가 방법

#### Step 1: 설정 추가

`app/config/scraper_config.py`에 새로운 스크래퍼 설정을 추가합니다.

```python
# app/config/scraper_config.py

class ScraperConfig(BaseModel):
    board_id: int
    base_url: str
    params: Dict[str, str | int]
    interval: int
    campus: Literal["sangmyung", "seoul"]

# 자동으로 환경변수를 가져옵니다
class EnvVars:
   def __getattr__(self, name):
       value = os.getenv(name)
       if value is None:
           raise AttributeError(f"Environment variable {name} not found")
       try:
           return int(value)
       except ValueError:
           return value

env = EnvVars()

SCRAPER_CONFIGS = {
   "main_board_sangmyung": ScraperConfig(
       board_id=env.MAIN_BOARD_SANGMYUNG_BOARD_ID,
       base_url="https://www.smu.ac.kr/kor/life/notice.do",
       params={
           "srCampus": "smu",
           "mode": "list",
           "articleLimit": 50,
           "article.offset": 0
       },
       interval=env.MAIN_BOARD_SANGMYUNG_INTERVAL,
       campus="sang"
   ),

       # 새로운 스크래퍼 설정 추가
    "new_board_scraper": ScraperConfig(
        board_id=env.NEW_BOARD_ID,,  # 새로운 board_id
        base_url="https://example.ac.kr/notice",
        params={
            "page": 1,
            "limit": 50
        },
        interval=env.NEW_BOARD_INTERVAL,  # 30분
        campus="seoul"  # 서울 캠퍼스
    )
}

def get_scraper_config(scraper_name: str) -> ScraperConfig:
    """스크래퍼 설정을 반환합니다."""
    return SCRAPER_CONFIGS.get(scraper_name)
```

#### Step 2: 스크래퍼 클래스 구현

`app/board/infra/scraper/`에 새로운 스크래퍼 클래스를 생성합니다.

```python
# app/board/infra/scraper/new_board_scraper.py
from app.board.infra.scraper.board_scraper_base import BoardScraper
from app.config.scraper_config import get_scraper_config

class NewBoardScraper(BoardScraper):
    def __init__(self, config_name: str):
        config = get_scraper_config(config_name)
        self.base_url = config.base_url
        self.board_id = config.board_id
        self.params = config.params

    def scrape(self) -> dict:
        """스크래핑 로직 구현"""
        # 웹사이트에서 데이터 수집 후
        # {"board_id": int, "count": int, "data": {post_id: ScrapedPost}} 형태로 반환
        pass
```

#### Step 3: 스크래퍼 등록

`app/board/infra/schedulers/scraper_initializer.py`에서 새 스크래퍼를 등록합니다.

```python
# 새 스크래퍼 import 추가
from app.board.infra.scraper.new_board_scraper import NewBoardScraper

def initialize_scrapers(scheduler: BoardScrapeScheduler):
    """모든 스크래퍼를 한번에 등록"""
    logger.info("스크래퍼 등록 시작")

    scrapers = [
        MainBoardScraper("main_board_sangmyung"),
        MainBoardScraper("main_board_seoul"),
        NewBoardScraper("new_board_scraper"),  # 새 스크래퍼 추가
    ]

    for scraper in scrapers:
        scheduler.add_board_scrape_job(scraper)
        scraper_name = f"{scraper.__class__.__name__}_{getattr(scraper, 'board_id', 'unknown')}"
        logger.info(f"{scraper_name} 등록 완료")

    logger.info(f"모든 스크래퍼 등록 완료: 총 {len(scrapers)}개")
```

#### Step 4: 데이터베이스 설정

새로운 게시판 정보를 데이터베이스에 추가합니다.

```sql
INSERT INTO board (id, campus, site, board_type, url)
VALUES (3, 'seoul', 'Example University', 'notice', 'https://example.ac.kr');
```

#### Step 5: 서버 재시작

```bash
uvicorn app.main:app --reload
```

서버가 시작되면 새로운 스크래퍼가 자동으로 등록되고 설정된 주기마다 실행됩니다.

### 4.2 게시물(Post) 스크래퍼 추가 방법

#### Step 1: 스크래퍼 코드 추가

`app/board/infra/scraper/posts/` 디렉토리에 IPostContentScraper 인터페이스를 구현한 새로운 스크래퍼 코드 추가

```python
class IPostContentScraper(ABC):
    """게시물 콘텐츠 스크래핑 인터페이스"""

    @abstractmethod
    async def extract_post_content_from_url(self, post: Post) -> SummaryProcessedPostDTO:
        """공개 API - 외부에서 호출"""
        pass

```

#### Step 2: 설정 추가

`app/board/infra/scraper/posts/scraper_factory.py`에 새로운 스크래퍼 설정을 추가합니다.

```python
# 환경변수에서 새로운 게시판 ID 가져오기
NEW_BOARD_ID = int(os.getenv("NEW_BOARD_ID"))

# _board_scraper_mapping에 새로운 매핑 추가
_board_scraper_mapping: Dict[int, type] = {
    MAIN_BOARD_SANGMYUNG_BOARD_ID: MainBoardPostScraper,
    MAIN_BOARD_SEOUL_BOARD_ID: MainBoardPostScraper,
    NEW_BOARD_ID: NewBoardPostScraper,  # 새로운 스크래퍼 추가
}
```

## 5. 개발 가이드라인

### 스크래퍼 개발 규칙

1. **BoardScraper 상속**: 모든 스크래퍼는 `BoardScraper`를 상속받아야 함
2. **scrape() 메서드 구현**: `{"board_id": int, "count": int, "data": dict}` 형식 반환 필수
3. **ScrapedPost 사용**: 수집된 데이터는 반드시 `ScrapedPost` 모델 사용
4. **설정 기반**: `get_scraper_config()`를 통해 설정 정보 로드

### 설정 파라미터

- **board_id**: 데이터베이스의 게시판 고유 ID
- **base_url**: 스크래핑할 웹사이트 URL
- **params**: 요청에 필요한 추가 파라미터
- **interval**: 스크래핑 실행 간격 (초 단위)
- **campus**: 캠퍼스 구분 ("sangmyung" 또는 "seoul")

## 6. 시작하기

### 1. 환경 설정

```bash
# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경변수 설정

프로젝트 루트에 `.env` 파일을 생성하고 다음 내용을 추가합니다:

```bash
# .env
DATABASE_URL=mysql+aiomysql://username:password@localhost:3306/database_name
```

**환경변수 설명:**

- `DATABASE_URL`: MySQL 데이터베이스 연결 문자열
  - 형식: `mysql+aiomysql://사용자명:비밀번호@호스트:포트/데이터베이스명`
  - 예시: `mysql+aiomysql://root:1234@localhost:3306/board_scraper`

### 3. 데이터베이스 설정

```bash
# MySQL 데이터베이스 생성
mysql -u root -p
CREATE DATABASE board_scraper;

# 테이블 생성 (SQLAlchemy 모델 기반)
# 서버 첫 실행 시 자동으로 생성됩니다
```

### 4. 서버 실행

```bash
# 개발 서버 실행 (자동 재시작)
uvicorn app.main:app --reload --port 8000

# 프로덕션 실행
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 5. 실행 확인

```bash
# 서버 상태 확인
curl http://localhost:8000/health

# 브라우저에서 확인
http://localhost:8000
```

**정상 실행 시 로그:**

```
INFO: 서버 시작: 스크래퍼 초기화 중...
INFO: 스크래퍼 등록 시작
INFO: MainBoardScraper_1 등록 완료
INFO: MainBoardScraper_2 등록 완료
INFO: 모든 스크래퍼 등록 완료: 총 2개
```

## 7. API 엔드포인트

```bash
# 서버 상태 확인
GET /health

# 응답 예시
{
  "status": "healthy",
  "active_jobs": 2
}
```

```

## 🤝 기여하기

1. Fork 프로젝트
2. Feature 브랜치 생성 (`git checkout -b feature/new-scraper`)
3. 변경사항 커밋 (`git commit -am 'feat:Add new scraper'`)
4. 브랜치에 Push (`git push origin feature/new-scraper`)
5. Pull Request 생성

## 📝 라이센스

이 프로젝트는 MIT 라이센스를 따릅니다.
```
