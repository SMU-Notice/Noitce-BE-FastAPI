from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.db import get_db
from app.services.test import get_test_message, add_test_message
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.test import MessageCreate, MessageResponse


router = APIRouter()

@router.get("/hello")
async def hello() -> dict:
    """
    기본적인 헬로 메시지를 반환하는 엔드포인트

    Returns:
        dict: {"message": "Hello, FastAPI"}
    """
    return {"message": "Hello, FastAPI"}

@router.get("/test-db", summary="Get Hello Message from DB", response_description="Fetches message from DB")
async def get_hello_message_from_db(db: AsyncSession = Depends(get_db)) -> dict:
    """
    데이터베이스에서 메시지를 조회한 후 반환하는 GET 엔드포인트

    Args:
        db (AsyncSession): 데이터베이스 세션 객체

    Returns:
        dict: {"message": "DB에서 조회된 메시지"} (DB에 저장된 메시지)
    """
    message = await get_test_message(db)
    return {"message": message}

@router.post("/test-db", summary="Post Hello Message to DB", response_description="Inserts a message into DB and returns it")
async def post_hello_message_to_db(message: MessageCreate, db: AsyncSession = Depends(get_db)) -> MessageResponse:
    """
    사용자가 제공한 메시지를 데이터베이스에 삽입하고, 삽입된 메시지를 반환하는 POST 엔드포인트

    Args:
        message (str): 사용자로부터 받은 메시지
        db (AsyncSession): 데이터베이스 세션 객체

    Returns:
        dict: {"message": "DB에 저장된 메시지"} (DB에 저장된 메시지)
    """
    inserted_message = await add_test_message(db, message.message)
    return MessageResponse(message=inserted_message)