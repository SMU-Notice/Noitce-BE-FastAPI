import logging
import os
from typing import Optional

from app.board.application.dto.summary_processed_post_dto import SummaryProcessedPostDTO
from app.board.domain.post import Post
from app.board.application.summary_service import SummaryService
from app.board.application.ocr_processor import OCRProcessor
from app.board.infra.scraper.posts.scraper_factory import PostScraperFactory

logger = logging.getLogger(__name__)

ENABLE_SUMMARY = os.getenv("ENABLE_SUMMARY", "false").lower() == "true"


class PostProcessingPipeline:
    """게시물 처리 파이프라인 - 스크래핑, OCR, 요약을 순차적으로 처리"""
    
    def __init__(
        self, 
        post_scraper_factory: Optional[PostScraperFactory] = None,
        ocr_processor: Optional[OCRProcessor] = None,
        summary_service: Optional[SummaryService] = None
    ):
        self.post_scraper_factory = post_scraper_factory or PostScraperFactory()
        self.ocr_processor = ocr_processor or OCRProcessor()
        self.summary_service = summary_service or SummaryService()

    async def process_post(self, post: Post) -> SummaryProcessedPostDTO:
        """
        게시물 전체 처리 플로우
        
        Args:
            post (Post): 처리할 게시물 객체
            
        Returns:
            SummaryProcessedPostDTO: 처리 완료된 게시물 DTO
        """
        try:
            logger.info("게시물 처리 시작 - 제목: %s, URL: %s", post.title, post.url)
            
            # 1단계: 텍스트 및 이미지 스크래핑
            scraped_dto = await self._scrape_post_content(post)
            
            # 2단계: OCR 처리
            ocr_processed_dto = await self._process_ocr(scraped_dto)
            
            # 3단계: 요약 처리
            final_dto = await self._process_summary(ocr_processed_dto)
            
            logger.info("게시물 처리 완료 - ID: %s", post.id)
            return final_dto
            
        except Exception as e:
            logger.error("게시물 처리 중 오류 발생 - URL: %s, 오류: %s", post.url, e)
            return SummaryProcessedPostDTO.create_with_post_only(post)

    async def _scrape_post_content(self, post: Post) -> SummaryProcessedPostDTO:
        """
        1단계: 게시물 스크래핑
        """
        logger.debug("스크래핑 단계 시작")
        
        scraper = self.post_scraper_factory.create_scraper_by_board_id(post)
        scraped_dto = await scraper.extract_post_content_from_url(post)
        
        logger.debug("스크래핑 단계 완료")
        return scraped_dto

    async def _process_ocr(self, dto: SummaryProcessedPostDTO) -> SummaryProcessedPostDTO:
        """
        2단계: OCR 처리
        """
        logger.debug("OCR 처리 단계 시작")
        
        if dto.post_picture is None:
            logger.debug("이미지가 없어 OCR 처리를 건너뜁니다")
            return dto
        
        processed_dto = await self.ocr_processor.process_dto(dto)
        logger.debug("OCR 처리 단계 완료")
        return processed_dto

    async def _process_summary(self, dto: SummaryProcessedPostDTO) -> SummaryProcessedPostDTO:
        """
        3단계: 요약 처리
        """
        if not ENABLE_SUMMARY:
            logger.debug("ENABLE_SUMMARY=False - 요약 처리를 건너뜁니다")
            return dto
        
        logger.debug("요약 처리 단계 시작")
        processed_dto = await self.summary_service.create_summary_processed_post(dto)
        logger.debug("요약 처리 단계 완료")
        return processed_dto