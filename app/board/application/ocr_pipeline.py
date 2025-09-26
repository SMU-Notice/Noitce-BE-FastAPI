import logging
import os
from app.board.domain.post_picture import PostPicture
from app.board.application.dto.summary_processed_post_dto import SummaryProcessedPostDTO
from app.board.application.ports.ocr_port import OCRPort
from app.board.application.summary_service import SummaryService
from app.board.infra.ocr.clova_ocr_adapter import ClovaOCRAdapter
from typing import Optional

logger = logging.getLogger(__name__)

ENABLE_SUMMARY = os.getenv("ENABLE_SUMMARY", "false").lower() == "true"


class OcrPipeline:
    """OCR 및 요약 처리를 담당하는 파이프라인"""
    
    def __init__(self, ocr_adapter: Optional[OCRPort] = None, summary_service: Optional[SummaryService] = None):
        self.ocr_adapter = ocr_adapter or ClovaOCRAdapter()
        self.summary_service = summary_service or SummaryService()
    
    async def process_dto(self, summary_processed_dto: SummaryProcessedPostDTO) -> SummaryProcessedPostDTO:
        """
        SummaryProcessedPostDTO를 받아서 이미지가 있으면 OCR 처리를 수행하고, 
        OCR 성공 시 요약도 함께 처리
        
        Args:
            summary_processed_dto: OCR 처리할 DTO
            
        Returns:
            SummaryProcessedPostDTO: OCR 및 요약 처리 완료된 DTO
        """
        if not summary_processed_dto.has_post_picture():
            logger.info("이미지가 없어서 OCR 처리를 건너뜁니다")
            return await self._process_summary(summary_processed_dto)
        
        post_picture = summary_processed_dto.post_picture
        
        # OCR 처리
        ocr_success = await self._process_ocr_for_picture(post_picture)
        
        if not ocr_success:
            logger.warning("OCR 처리 실패로 이미지를 DTO에서 제거합니다")
            # OCR 실패 시 post_picture를 None으로 설정
            summary_processed_dto.post_picture = None
        
        # 요약 처리 (OCR 성공/실패와 관계없이)
        return await self._process_summary(summary_processed_dto)
    
    async def _process_ocr_for_picture(self, post_picture: PostPicture) -> bool:
        """
        PostPicture에 대해 OCR 처리를 수행
        
        Args:
            post_picture: OCR 처리할 PostPicture 객체
            
        Returns:
            bool: OCR 처리 성공 여부
        """
        if not post_picture or not post_picture.url:
            logger.warning("OCR 처리 조건이 충족되지 않음 - PostPicture 또는 URL이 없음")
            return False
            
        logger.info(f"OCR 처리 시작 - 이미지 URL: {post_picture.url}")
        
        try:
            # OCR 어댑터를 사용하여 텍스트 추출
            extracted_text = self.ocr_adapter.extract_text_from_image_pipeline(post_picture.url)
            
            if extracted_text:
                # 원본 OCR 텍스트 저장
                post_picture.original_ocr_text = extracted_text
                logger.info(f"OCR 처리 완료 - 추출된 텍스트 길이: {len(extracted_text)}자")
                return True
            else:
                logger.warning("OCR 결과가 비어있습니다")
                post_picture.picture_summary = "실패"
                return False
                
        except Exception as e:
            logger.error(f"OCR 처리 중 오류 발생: {e}")
            post_picture.picture_summary = "실패"
            return False
    
    async def _process_summary(self, dto: SummaryProcessedPostDTO) -> SummaryProcessedPostDTO:
        """
        요약 처리 수행
        
        Args:
            dto: 요약 처리할 DTO
            
        Returns:
            SummaryProcessedPostDTO: 요약 처리 완료된 DTO
        """
        if not ENABLE_SUMMARY:
            logger.debug("ENABLE_SUMMARY=False - 요약 처리를 건너뜁니다")
            return dto
        
        logger.debug("요약 처리 단계 시작")
        processed_dto = await self.summary_service.create_summary_processed_post(dto)
        logger.debug("요약 처리 단계 완료")
        return processed_dto