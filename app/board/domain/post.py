from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional

from dataclasses import dataclass
from typing import Optional, List
from datetime import date, time, datetime, timezone
from abc import ABC, abstractmethod


@dataclass
class Post:
   """게시글 도메인 객체"""
   board_id: int
   original_post_id: int
   post_type: str
   title: str
   url: str
   posted_date: date
   view_count: int
   has_reference: bool
   id: Optional[int] = None
   content_summary: Optional[str] = "N/A"
   original_content: Optional[str] = None  # 원본 콘텐츠 (DB 저장 안함)
   
   def to_dict(self) -> dict:
       """Domain Entity를 dict로 변환"""
       return {
           'id': self.id,
           'board_id': self.board_id,
           'original_post_id': self.original_post_id,
           'type_': self.post_type,  # DB 모델의 필드명에 맞춤
           'title': self.title,
           'content_summary': self.content_summary,
           'view_count': self.view_count,
           'url': self.url,
           'has_reference': self.has_reference,
           'posted_date': self.posted_date,
           'scraped_at': datetime.now(timezone.utc)
           # original_content는 DB에 저장하지 않으므로 제외
       }
   
   @classmethod
   def from_dict(cls, data: dict) -> 'Post':
       """dict를 Domain Entity로 변환"""
       return cls(
           id=data.get('id'),
           board_id=data.get('board_id'),
           original_post_id=data.get('original_post_id'),
           post_type=data.get('type_'),  # DB 모델의 type_ 필드에서 변환
           title=data.get('title'),
           content_summary=data.get('content_summary', 'N/A'),
           view_count=data.get('view_count'),
           url=data.get('url'),
           has_reference=data.get('has_reference'),
           posted_date=data.get('posted_date'),
           original_content=None  # DB에서 가져올 때는 None
       )