import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession


# .env 파일 로드
load_dotenv()

# 환경 변수에서 DATABASE_URL 가져오기
DATABASE_URL = os.getenv("DATABASE_URL")

# Base 선언 (모든 모델의 베이스 클래스)
Base = declarative_base()

# 비동기 SQLAlchemy 엔진
engine = create_async_engine(
    DATABASE_URL, 
    echo=True, 
    pool_recycle=1800,  # 30분마다 커넥션 재활용 (MySQL 대비 설정)
    pool_pre_ping=True   # 연결이 유효한지 미리 확인 (끊어진 연결 방지)
)

# 비동기 세션 생성
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# get_db() 함수 수정 (직접 AsyncSession 반환)
async def get_db():
    async with AsyncSessionLocal() as session:  # 비동기 세션을 async with로 관리
        yield session  # 세션 객체 반환