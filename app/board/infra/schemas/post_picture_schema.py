from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PostPictureSchema(BaseModel):
    """PostPicture 변환용 Schema"""
    id: Optional[int] = None
    post_id: Optional[int] = None
    url: str
    picture_summary: Optional[str] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True  # SQLAlchemy 모델에서 자동 변환