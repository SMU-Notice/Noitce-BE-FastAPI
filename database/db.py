import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import AsyncGenerator


# .env 파일 로드
load_dotenv()

# 환경 변수에서 DATABASE_URL 가져오기
DATABASE_URL = os.getenv("DATABASE_URL")

# 비동기 SQLAlchemy 엔진
engine = create_async_engine(DATABASE_URL, echo=True)

# 비동기 세션 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

# ORM 모델의 베이스 클래스
Base = declarative_base()

# 비동기 DB 세션을 가져오는 종속성 주입 함수
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session  # 세션을 반환하고, 세션이 끝나면 자동으로 닫힙니다.
