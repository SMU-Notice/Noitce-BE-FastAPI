# domains/board/infrastructure/scrapers/models/scraped_post.py
from pydantic import BaseModel, field_validator, Field
from typing import Optional
from datetime import date, datetime

class ScrapedPost(BaseModel):
    """게시물 데이터를 위한 Pydantic 모델"""
    original_post_id: str
    title: str
    date: str
    campus: str
    post_type: str
    view_count: str
    url: str
    has_reference: bool

    @field_validator('original_post_id')
    @classmethod
    def validate_original_post_id(cls, v):
        if not v:
            raise ValueError("original_post_id는 빈 문자열이 될 수 없습니다.")
        return v
