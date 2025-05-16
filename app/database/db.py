import logging
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import AsyncGenerator

# 로깅 설정: SQLAlchemy 쿼리 로그 끄기 (echo=True 상태에서도)
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.dialects').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.orm').setLevel(logging.WARNING)

# .env 파일 로드
load_dotenv()

# 환경 변수에서 DATABASE_URL 가져오기
DATABASE_URL = os.getenv("DATABASE_URL")

# Base 선언 (모든 모델의 베이스 클래스)
Base = declarative_base()

# 비동기 SQLAlchemy 엔진
engine = create_async_engine(
    DATABASE_URL, 
    echo=False,              # 디버깅용으로 SQL 출력 설정 (필요시 False로)
    pool_recycle=1800,      # 30분마다 커넥션 재활용
    pool_pre_ping=True      # 연결이 유효한지 미리 확인
)

# 비동기 세션 생성
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# get_db() 함수 (의존성 주입용)
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
