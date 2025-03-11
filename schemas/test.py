# schemas/test.py
from pydantic import BaseModel

class MessageCreate(BaseModel):
    message: str  # 클라이언트가 보낼 메시지

class MessageResponse(BaseModel):
    message: str  # 클라이언트에게 반환할 메시지
