import logging
from typing import List, Dict, Any, Optional
from app.board.application.post_classifier import PostClassifier
from app.board.application.post_processor import PostProcessor
from app.board.application.converters.post_converter import PostConverter
from app.board.application.dto.classification_result import ClassificationResult
from app.board.domain.post import Post
from app.board.application.dto.new_post_notification import NewPostNotificationDTO
from app.board.application.interfaces.new_post_sender import INewPostSender

logger = logging.getLogger(__name__)

class ScrapedPostManager:
    """
    스크래핑된 게시물 처리를 총괄 관리하는 클래스
    """
    
    def __init__(self, 
                 post_classifier: PostClassifier = None,
                 new_post_sender: INewPostSender = None):
        self.classifier = post_classifier or PostClassifier()
        self.new_post_sender = new_post_sender
    
    async def manage_scraped_posts(self, scraped_posts: Dict[str, Any]) -> List[Post]:
        """
        스크래핑된 게시물 처리 메인 메서드
        
        Parameters:
        - scraped_posts: 스크래핑된 raw 데이터 (ScrapedPost 형태)
        
        Returns:
        - List[Post]: 새로 저장된 게시물 목록
        """
        logger.info("manage_scraped_posts: 시작")
        
        # 1. Raw 데이터 → 도메인 객체 변환
        domain_data = PostConverter.convert_scraped_data_to_domain(scraped_posts)
        
        # 2. 분류 후 새로운 게시물 목록 받음 (존재하면)
        notification_dto: Optional[NewPostNotificationDTO] = await self.classifier.classify_posts(domain_data)
        
        # 4. 외부 알림 전송 (새 게시물이 있으면)
        if notification_dto and self.new_post_sender:
            try:
                logger.info("새 게시물 외부 알림 전송 시작 - board_id: %d, post_types: %s", 
                           notification_dto.board_id, notification_dto.post_types)
                await self.new_post_sender.send_notification(notification_dto)
                logger.info("새 게시물 외부 알림 전송 완료")
            except Exception as e:
                logger.error("새 게시물 외부 알림 전송 실패: %s", e)
        
        return notification_dto