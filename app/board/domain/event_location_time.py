from dataclasses import dataclass
from typing import Optional, List
from datetime import date, datetime, timezone
from abc import ABC, abstractmethod


@dataclass
class EventLocationTime:
    """이벤트 장소 및 날짜 정보 도메인 객체"""
    id: Optional[int] = None
    post_id: Optional[int] = None
    original_post_id: Optional[int] = None
    location: str = ""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    
    def to_dict(self) -> dict:
        """Domain Entity를 dict로 변환"""
        return {
            'id': self.id,
            'post_id': self.post_id,
            'location': self.location,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'created_at': datetime.now(timezone.utc)
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'EventLocationTime':
        """dict를 Domain Entity로 변환"""
        return cls(
            id=data.get('id'),
            post_id=data.get('post_id'),
            original_post_id=data.get('original_post_id'),
            location=data.get('location', ''),
            start_date=data.get('start_date'),
            end_date=data.get('end_date')
        )