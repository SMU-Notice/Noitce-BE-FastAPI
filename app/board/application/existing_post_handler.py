import logging
from typing import List
from sqlalchemy.exc import SQLAlchemyError
from app.board.infra.repository.post_repo import PostRepository
from app.board.domain.post import Post

logger = logging.getLogger(__name__)


class ExistingPostHandler:
    """기존 게시물 처리 전용 클래스"""
    
    def __init__(self, post_repo: PostRepository = None):
        self.post_repo = post_repo or PostRepository()
    
    async def handle_existing_posts(self, existing_posts_updates: List[Post]) -> bool:
        """
        기존 게시물들을 처리 (조회수만 업데이트)
        
        Parameters:
        - existing_posts_updates: 업데이트할 Post 객체 목록 (id와 view_count 포함)
        
        Returns:
        - bool: 처리 성공 여부
        """
        if not existing_posts_updates:
            logger.info("ExistingPostHandler: 처리할 기존 게시물이 없습니다.")
            return True
        
        logger.info("ExistingPostHandler: 기존 게시물 조회수 업데이트 시작, 개수: %d", len(existing_posts_updates))
        
        try:
            # 조회수만 업데이트 (content_summary는 건드리지 않음)
            await self._update_view_counts_only(existing_posts_updates)
            
            # TODO: 나중에 추가될 수 있는 처리들
            # await self._track_view_count_changes(existing_posts_updates)  # 조회수 변화 추적
            # await self._update_popularity_score(existing_posts_updates)   # 인기도 점수 업데이트
            # await self._check_trending_posts(existing_posts_updates)      # 트렌딩 게시물 체크
            
            logger.info("ExistingPostHandler: 기존 게시물 조회수 업데이트 완료")
            return True
            
        except Exception as e:
            logger.error("ExistingPostHandler: 기존 게시물 처리 실패: %s", e)
            return False
    
    async def _update_view_counts_only(self, existing_posts: List[Post]) -> None:
        """기존 게시물의 조회수만 배치 업데이트"""
        try:
            # 조회수만 업데이트하는 배치 메서드 사용
            await self.post_repo.update_view_counts_only(existing_posts)
            logger.info("ExistingPostHandler: %d개 기존 게시물 조회수 업데이트 완료", len(existing_posts))
        except SQLAlchemyError as e:
            logger.error("ExistingPostHandler: 조회수 업데이트 실패: %s", e)
            raise