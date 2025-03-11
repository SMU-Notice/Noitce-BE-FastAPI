from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import insert
from models.test import TestModel

# DB에서 Hello 메시지를 가져오는 서비스 함수 (비동기)
async def get_test_message(db: AsyncSession) -> str:
    result = await db.execute(select(TestModel).limit(1))
    message = result.scalars().first()
    if message:
        return message.string
    return "Not Hello, FastAPI!"  # 기본 메시지


# DB에 새로운 Hello 메시지를 추가하는 서비스 함수 (비동기)
async def add_test_message(db: AsyncSession, message: str) -> str:
    # 새로운 레코드를 삽입
    stmt = insert(TestModel).values(string=message)
    await db.execute(stmt)
    await db.commit()  # 트랜잭션 커밋
    
    return f"Message '{message}' added to the database!"