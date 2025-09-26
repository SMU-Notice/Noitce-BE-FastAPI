from abc import ABC, abstractmethod
from typing import Optional
from app.board.domain.event_location_time import EventLocationTime
from app.board.domain.post import Post

class SummaryPort(ABC):
    """요약 서비스 아웃바운드 포트"""
    
    @abstractmethod
    async def summarize_post_content(self, post: Post) -> Post:
        """
        게시물 본문을 요약합니다.
        
        Args:
            content: 요약할 게시물 콘텐츠
            
        Returns:
            Post: 요약 결과
        """
        pass
    
    @abstractmethod
    async def extract_structured_location_info(self, summary_content: str) -> Optional[EventLocationTime]:
        """
        요약된 내용에서 날짜, 시간, 장소 정보를 추출합니다.
        
        Args:
            summary_content: 요약된 내용
            
        Returns:
            EventLocationTime: 추출된 위치 및 시간 정보 (없으면 None)
        """
        pass