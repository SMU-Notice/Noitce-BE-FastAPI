import logging
from typing import List, Dict, Any
from app.board.application.post_classifier import PostClassifier
from app.board.application.post_processor import PostProcessor
from app.board.application.converters.post_converter import PostConverter
from app.board.application.dto.classification_result import ClassificationResult
from app.board.domain.post import Post as PostVO

logger = logging.getLogger(__name__)


class ScrapedPostManager:
    """
    스크래핑된 게시물 처리를 총괄 관리하는 클래스
    """
    
    def __init__(self, 
                 post_classifier: PostClassifier = None,
                 post_processor: PostProcessor = None):
        self.classifier = post_classifier or PostClassifier()
        self.processor = post_processor or PostProcessor()
    
    async def manage_scraped_posts(self, scraped_posts: Dict[str, Any]) -> List[PostVO]:
        """
        스크래핑된 게시물 처리 메인 메서드
        
        Parameters:
        - scraped_posts: 스크래핑된 raw 데이터 (ScrapedPost 형태)
        
        Returns:
        - List[PostVO]: 새로 저장된 게시물 목록
        """
        logger.info("manage_scraped_posts: 시작")
        
        # 1. Raw 데이터 → 도메인 객체 변환
        domain_data = PostConverter.convert_scraped_data_to_domain(scraped_posts)
        
        # 2. 분류
        classification_result: ClassificationResult = await self.classifier.classify_posts(domain_data)
        
        # 3. 처리 (조건부)
        await self.processor.process_posts(classification_result)
        
        logger.info("manage_scraped_posts: 완료, 신규 게시물 개수=%d", len(classification_result.new_posts))
        return classification_result.new_posts