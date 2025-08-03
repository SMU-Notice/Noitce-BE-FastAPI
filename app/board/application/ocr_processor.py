import logging
from app.board.domain.post_picture import PostPicture
from app.board.application.dto.summary_processed_post_dto import SummaryProcessedPostDTO
from app.board.application.ports.ocr_port import OCRPort
from app.board.infra.ocr.clova_ocr_adapter import ClovaOCRAdapter
from typing import Optional

logger = logging.getLogger(__name__)

class OCRProcessor:
    """OCR 처리를 담당하는 서비스"""
    
    def __init__(self, ocr_adapter: Optional[OCRPort] = None):
        self.ocr_adapter = ocr_adapter or ClovaOCRAdapter()
    
    async def process_dto(self, summary_processed_dto: SummaryProcessedPostDTO) -> SummaryProcessedPostDTO:
        """
        SummaryProcessedPostDTO를 받아서 이미지가 있으면 OCR 처리를 수행
        
        Args:
            summary_processed_dto: OCR 처리할 DTO
            
        Returns:
            SummaryProcessedPostDTO: OCR 처리 완료된 DTO
        """
        if not summary_processed_dto.has_post_picture():
            logger.info("이미지가 없어서 OCR 처리를 건너뜁니다")
            return summary_processed_dto
        
        post_picture = summary_processed_dto.post_picture
        
        # OCR 처리
        ocr_success = await self._process_ocr_for_picture(post_picture)
        
        if not ocr_success:
            logger.warning("OCR 처리 실패로 이미지를 DTO에서 제거합니다")
            # OCR 실패 시 post_picture를 None으로 설정
            summary_processed_dto.post_picture = None
        
        return summary_processed_dto
    
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
            extracted_text = self.ocr_adapter.extract_text_from_image(post_picture.url)
            
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