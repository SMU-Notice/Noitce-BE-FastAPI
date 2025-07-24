import logging
from typing import List, Dict, Optional
from app.board.application.dto.classification_result import ClassificationResult
from app.board.application.new_post_handler import NewPostHandler
from app.board.application.existing_post_handler import ExistingPostHandler
from app.board.domain.post import Post
from app.board.application.dto.new_post_notification import NewPostNotificationDTO

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
    
    async def process_posts(self, classification_result: ClassificationResult) -> Optional[NewPostNotificationDTO]:
        """
        분류된 게시물들을 처리하고 알림 DTO를 반환
        
        Parameters:
        - classification_result: PostClassifier에서 분류된 결과
        
        Returns:
        - Optional[NewPostNotificationDTO]: 새 게시물이 있으면 알림 DTO, 없으면 None
        """
        logger.info("PostProcessor: 게시물 처리 시작")
        
        new_post_notification : NewPostNotificationDTO = None
        
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
            
            # 신규 게시물 저장 (DB에서 생성된 ID 포함하여 반환)
            saved_posts = await self.new_post_handler.handle_new_posts(
                classification_result.new_posts
            )
            
            # 외부 알림용 DTO 변환 (저장 성공 후)
            if saved_posts:
                new_post_notification = self._convert_to_notification_dto(saved_posts)
                if new_post_notification:
                    logger.info("외부 알림용 DTO 생성 완료")
                else:
                    logger.warning("외부 알림용 DTO 생성 실패")
        
        logger.info("PostProcessor: 게시물 처리 완료")
        
        return new_post_notification
    
    def _convert_to_notification_dto(self, saved_posts: List[Post]) -> Optional[NewPostNotificationDTO]:
        """
        저장된 Post 리스트를 외부 알림용 DTO로 변환
        
        Args:
            saved_posts: DB에 저장된 게시물 리스트 (ID 포함)
            
        Returns:
            Optional[NewPostNotificationDTO]: 외부 알림용 DTO, 변환 실패 시 None
        """
        if not saved_posts:
            logger.warning("변환할 게시물이 없습니다")
            return None
        
        try:
            # 첫 번째 게시물의 board_id 사용 (모든 게시물이 같은 보드라고 가정)
            board_id = saved_posts[0].board_id
            
            # post_type별로 그룹핑하여 ID 리스트 생성
            post_types: Dict[str, List[int]] = {}
            
            for post in saved_posts:
                # board_id 일관성 검증
                if post.board_id != board_id:
                    logger.warning("서로 다른 board_id를 가진 게시물들: %d vs %d", 
                                 board_id, post.board_id)
                
                # post_type별로 ID 그룹핑
                post_type = post.post_type
                if post_type not in post_types:
                    post_types[post_type] = []
                
                # DB에서 생성된 ID 사용
                if post.id:
                    post_types[post_type].append(post.id)
                else:
                    logger.warning("ID가 없는 게시물 발견: %s", post.title)
            
            # 빈 post_types 제거
            post_types = {k: v for k, v in post_types.items() if v}
            
            if not post_types:
                logger.warning("유효한 게시물 ID가 없어 알림을 생성할 수 없습니다")
                return None
            
            new_posts_dto = NewPostNotificationDTO(
                board_id=board_id,
                post_types=post_types
            )
            
            logger.info("알림 DTO 변환 완료 - board_id: %d, post_types: %s", 
                       board_id, post_types)
            
            return new_posts_dto
            
        except Exception as e:
            logger.error("게시물을 알림 DTO로 변환 중 오류: %s", e)
            return None
