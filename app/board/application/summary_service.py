import logging
from app.board.application.ports.summary_port import SummaryPort
from app.board.application.dto.scraped_content import ScrapedContent
from app.board.infra.adapters.openai_summary_adapter import SummarizedScrapedContent
from app.board.infra.adapters.openai_summary_adapter import OpenAISummaryAdapter
from app.board.domain.event_location_time import EventLocationTime
from app.board.application.dto.processed_post_dto import ProcessedPostDTO
from app.board.domain.post import Post
from typing import Optional

logger = logging.getLogger(__name__)

class SummaryService:
    """요약 서비스 - 요약과 Location 정보 추출을 담당"""
    
    def __init__(self, summary_adapter: SummaryPort = None):
        self.summary_adapter = summary_adapter or OpenAISummaryAdapter()
    
    async def create_summary_and_location(self, post: Post, content: ScrapedContent) -> ProcessedPostDTO:
        """
        Post와 스크래핑된 콘텐츠를 받아서 요약과 Location 정보를 추출하여 ProcessedPostDTO로 반환합니다.
        
        Args:
            post: 처리할 Post 객체
            content: 스크래핑된 원본 콘텐츠
            
        Returns:
            ProcessedPostDTO: Post, Location 정보를 포함한 처리 결과
        """
        try:
            logger.info("Post 요약 및 Location 추출을 시작합니다.")
            
            # 1. 요약 생성
            summary_result = await self.summary_adapter.summarize_post_content(content)
            
            # 2. Post 객체 업데이트
            if summary_result.is_successful:
                post.content_summary = summary_result.summary
                logger.info("Post 요약이 완료되었습니다.")
            else:
                post.content_summary = content.text
                logger.warning("Post 요약에 실패했습니다: %s", summary_result.error_message)
            
            # 3. Location 정보 추출 (요약이 성공한 경우에만)
            location_entity = None

            # if summary_result.is_successful and summary_result.summary:
            #     try:
            #         location_entity = await self.summary_adapter.extract_structured_location_info(summary_result.summary)
            #         if location_entity:
            #             location_entity.original_post_id = str(post.original_post_id)
            #             logger.info(f"위치 정보 추출 성공: {location_entity.location}")
            #         else:
            #             logger.info("위치 정보 추출 실패 또는 위치 정보 없음")
            #     except Exception as e:
            #         logger.error(f"위치 정보 추출 중 오류 발생: {e}")
            
            # 4. ProcessedPostDTO 생성 및 반환
            return ProcessedPostDTO.create_complete(
                post=post,
                location=location_entity,
                ocr_entity=None  # OCR은 아직 구현되지 않음
            )
                
        except Exception as e:
            logger.error("Post 처리 중 예상치 못한 오류 발생: %s", str(e))
            # 오류 발생 시 Post만 포함한 DTO 반환
            return ProcessedPostDTO.create_with_post_only(post)