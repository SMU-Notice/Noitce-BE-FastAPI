from abc import ABC, abstractmethod
from typing import Dict
from app.board.domain.post import Post
from app.board.application.dto.summary_processed_post_dto import SummaryProcessedPostDTO

class IPostContentScraper(ABC):
    """게시물 콘텐츠 스크래핑 인터페이스"""
    
    @abstractmethod
    async def extract_post_from_url(self, post: Post) -> SummaryProcessedPostDTO:
        """공개 API - 외부에서 호출"""
        pass
    
    @abstractmethod
    async def _scrape_content_and_images(self, post: Post) -> Dict:
        """내부 메서드 - 1단계"""
        pass
    
    @abstractmethod
    async def _process_ocr_if_needed(self, summary_processed_dto: SummaryProcessedPostDTO) -> SummaryProcessedPostDTO:
        """내부 메서드 - 2단계"""
        pass
    
    @abstractmethod
    async def _process_summary(self, summary_processed_dto: SummaryProcessedPostDTO) -> SummaryProcessedPostDTO:
        """내부 메서드 - 3단계"""
        pass