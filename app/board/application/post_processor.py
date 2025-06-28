import logging
from app.board.application.dto.classification_result import ClassificationResult
from app.board.application.new_post_handler import NewPostHandler
from app.board.application.existing_post_handler import ExistingPostHandler

logger = logging.getLogger(__name__)


class PostProcessor:
    """
    게시물 처리 조율 클래스
    신규/기존 게시물 처리기들을 내부에서 관리하고 조건부 실행
    """
    
    def __init__(self, 
                 new_post_handler: NewPostHandler = None,
                 existing_post_handler: ExistingPostHandler = None):
        self.new_post_handler = new_post_handler or NewPostHandler()
        self.existing_post_handler = existing_post_handler or ExistingPostHandler()
    
    async def process_posts(self, classification_result: ClassificationResult) -> None:
        """
        분류된 게시물들을 처리
        
        Parameters:
        - classification_result: PostClassifier에서 분류된 결과
        """
        logger.info("PostProcessor: 게시물 처리 시작")
        
        # 기존 게시물 처리 (조건부 실행)
        if classification_result.has_existing_posts:
            logger.info("기존 게시물 조회수 업데이트 시작, 대상 개수: %d", 
                       len(classification_result.existing_posts_updates))
            await self.existing_post_handler.handle_existing_posts(
                classification_result.existing_posts_updates
            )
        
        # 신규 게시물 처리 (조건부 실행)
        if classification_result.has_new_posts:
            logger.info("신규 게시물 DB 저장 시작, 대상 개수: %d", 
                       len(classification_result.new_posts))
            await self.new_post_handler.handle_new_posts(
                classification_result.new_posts
            )
        
        logger.info("PostProcessor: 게시물 처리 완료")