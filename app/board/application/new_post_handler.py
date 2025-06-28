import logging
from typing import List
from sqlalchemy.exc import SQLAlchemyError
from app.board.infra.repository.post_repo import PostRepository
from app.board.domain.post import Post as PostVO

logger = logging.getLogger(__name__)


class NewPostHandler:
    """새로운 게시물 처리 전용 클래스"""
    
    def __init__(self, post_repo: PostRepository = None):
        self.post_repo = post_repo or PostRepository()
    
    async def handle_new_posts(self, new_posts: List[PostVO]) -> None:
        """
        새로운 게시물들을 처리 (저장)
        
        Parameters:
        - new_posts: 저장할 신규 PostVO 객체 목록
        """
        try:
            await self.post_repo.create_posts(new_posts)
            logger.info("NewPostHandler: %d개 신규 게시물 저장 완료", len(new_posts))
        except SQLAlchemyError as e:
            logger.error("NewPostHandler: 저장 실패: %s", e)
            raise