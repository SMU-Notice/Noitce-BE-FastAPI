import logging
from app.board.application.ports.summary_port import SummaryPort
from app.board.infra.adapters.openai_summary_adapter import OpenAISummaryAdapter
from app.board.application.dto.summary_processed_post_dto import SummaryProcessedPostDTO
from app.board.application.dto.summary_processed_post_dto import SummaryProcessedPostDTO
from typing import Optional

logger = logging.getLogger(__name__)

class SummaryService:
    """요약 서비스 - 요약과 Location 정보 추출을 담당"""
    
    def __init__(self, summary_adapter: SummaryPort = None):
        self.summary_adapter = summary_adapter or OpenAISummaryAdapter()
    
    async def create_summary_processed_post(self, summary_processed_dto:SummaryProcessedPostDTO) -> SummaryProcessedPostDTO:
        """
        SummaryProcessedPostDTO를 받아서 요약 처리를 수행하고 반환합니다.
        
        Args:
            summary_processed_dto: 요약 처리할 SummaryProcessedPostDTO
            
        Returns:
            SummaryProcessedPostDTO: 요약 처리된 DTO
        """
        try:
            logger.info("Post 요약 시작합니다.")
            
            # 1. 요약 생성
            summary_processed_dto.post = await self.summary_adapter.summarize_post_content(summary_processed_dto.post)

            if summary_processed_dto.post.content_summary != "실패":
                content_summary_log = summary_processed_dto.post.content_summary[:10] + ("..." if len(summary_processed_dto.post.content_summary) > 10 else "")
                logger.info(f"Post 본문 요약이 완료되었습니다. content_summary: {content_summary_log}")
            else:
                logger.warning("Post 본문 요약에 실패했습니다: %s", summary_processed_dto.post.title)

            # 2. 만약 사진이 존재한다면 사진 요약
            if summary_processed_dto.has_post_picture():
                logger.info("게시물에 사진이 존재합니다. 사진 요약을 시작합니다.")
                
                summary_processed_dto.post_picture = await self.summary_adapter.summarize_ocr_content(summary_processed_dto.post_picture)
                
                if summary_processed_dto.post_picture and summary_processed_dto.post_picture.picture_summary == "실패":
                    logger.warning("사진 요약 실패 - PostPicture를 DTO에서 제거")
                    summary_processed_dto.post_picture = None
                elif summary_processed_dto.post_picture:
                    logger.info(f"사진 요약 성공: {summary_processed_dto.post_picture.picture_summary[:50]}...")

            
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
            return summary_processed_dto
        
        except Exception as e:
            logger.error("Post 처리 중 예상치 못한 오류 발생: %s", str(e))
            return SummaryProcessedPostDTO(post=summary_processed_dto.post)