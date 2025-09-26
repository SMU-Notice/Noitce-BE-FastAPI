import logging
from typing import Optional

from app.board.application.dto.summary_processed_post_dto import SummaryProcessedPostDTO
from app.board.domain.post import Post
from app.board.application.ocr_pipeline import OcrPipeline
from app.board.infra.scraper.posts.scraper_factory import PostScraperFactory

logger = logging.getLogger(__name__)


class PostProcessingPipeline:
    """게시물 처리 파이프라인 - 스크래핑, OCR(요약 포함)을 순차적으로 처리"""
    
    def __init__(
        self, 
        post_scraper_factory: Optional[PostScraperFactory] = None,
        ocr_pipeline: Optional[OcrPipeline] = None
    ):
        self.post_scraper_factory = post_scraper_factory or PostScraperFactory()
        self.ocr_pipeline = ocr_pipeline or OcrPipeline()

    async def process_post(self, post: Post) -> SummaryProcessedPostDTO:
        """
        게시물 전체 처리 플로우
        
        Args:
            post (Post): 처리할 게시물 객체
            
        Returns:
            SummaryProcessedPostDTO: 처리 완료된 게시물 DTO (OCR 및 요약 포함)
        """
        try:
            logger.info("게시물 처리 시작 - 제목: %s, URL: %s", post.title, post.url)
            
            # 1단계: 텍스트 및 이미지 스크래핑
            scraped_dto = await self._scrape_post_content(post)
            
            # 2단계: OCR 처리 (요약 포함)
            final_dto = await self._process_ocr_and_summary(scraped_dto)
            
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

    async def _process_ocr_and_summary(self, dto: SummaryProcessedPostDTO) -> SummaryProcessedPostDTO:
        """
        2단계: OCR 처리 및 요약 처리 (OcrPipeline에서 모두 처리)
        """
        logger.debug("OCR 및 요약 처리 단계 시작")
        
        processed_dto = await self.ocr_pipeline.process_dto(dto)
        logger.debug("OCR 및 요약 처리 단계 완료")
        return processed_dto