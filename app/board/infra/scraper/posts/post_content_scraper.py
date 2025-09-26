from abc import ABC, abstractmethod
from typing import Dict
from app.board.domain.post import Post
from app.board.application.dto.summary_processed_post_dto import SummaryProcessedPostDTO

class IPostContentScraper(ABC):
    """게시물 콘텐츠 스크래핑 인터페이스"""
    
    @abstractmethod
    async def extract_post_content_from_url(self, post: Post) -> SummaryProcessedPostDTO:
        """공개 API - 외부에서 호출"""
        pass
