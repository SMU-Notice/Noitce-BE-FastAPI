import logging
from app.board.application.ports.summary_port import SummaryPort
from app.board.application.dto.scraped_content import ScrapedContent
from app.board.infra.adapters.openai_summary_adapter import SummarizedScrapedContent
from app.board.infra.adapters.openai_summary_adapter import OpenAISummaryAdapter
from app.board.domain.event_location_time import EventLocationTime
from typing import Optional

logger = logging.getLogger(__name__)

class SummaryService:
    """요약 서비스 - 1차 요약을 담당"""
    
    def __init__(self, summary_adapter: SummaryPort = None):
        self.summary_adapter = summary_adapter or OpenAISummaryAdapter()
    
    async def create_summary(self, content: ScrapedContent) -> SummarizedScrapedContent:
        """
        스크래핑된 콘텐츠를 요약합니다.
        
        Args:
            content: 스크래핑된 원본 콘텐츠
            
        Returns:
            SummarizedScrapedContent: 요약 결과
        """

        try:
            logger.info("콘텐츠 요약을 시작합니다.")
            summary_result: SummarizedScrapedContent = await self.summary_adapter.summarize_post_content(content)

            event_location_time: Optional[EventLocationTime] = None
            
            if summary_result.is_successful:
                logger.info("콘텐츠 요약이 완료되었습니다.")

                # 장소 추출
                event_location_time = await self.summary_adapter.extract_event_location_time(summary_result.summary)
            else:
                logger.warning("콘텐츠 요약에 실패했습니다: %s", summary_result.error_message)

            # 장소 추출

            
            return summary_result
                
        except Exception as e:
            logger.error("요약 중 예상치 못한 오류 발생: %s", str(e))
            return SummarizedScrapedContent.failure(
                original_content=str(content.text) if hasattr(content, 'text') else str(content),
                error_message=f"요약 처리 중 오류 발생: {str(e)}"
            )