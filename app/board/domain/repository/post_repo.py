from abc import ABC, abstractmethod
from typing import List
from app.board.domain.post import Post

class IPostRepository(ABC):
    """Interface for Post Repository"""

    @abstractmethod
    async def create_posts(self, posts: List[Post]) -> None:
        """여러 개의 게시글을 저장합니다."""
        pass

    @abstractmethod
    async def read_posts_desc_by_id(self, board_id: int, record_count: int) -> List[Post]:
        """특정 게시판의 게시글을 ID 기준 내림차순으로 조회합니다."""
        pass

    @abstractmethod
    async def update_multiple_posts(self, updates: List[dict]) -> None:
        """여러 게시글의 일부 필드를 업데이트합니다."""
        pass

    @abstractmethod
    async def upsert_posts_and_return_new(self, posts: List[Post]) -> List[Post]:
        """게시글들을 upsert하고 새로 생성된 게시글들만 반환합니다.
        
        Args:
            posts: upsert할 게시글 목록
            
        Returns:
            새로 생성된 게시글들의 목록 (기존에 존재하던 게시글은 제외)
        """
        pass

    @abstractmethod
    async def find_by_original_ids(self, board_id: int, original_ids: List[str]) -> List[Post]:
        """특정 게시판에서 original_id 리스트에 해당하는 게시물들을 조회합니다.
        
        Args:
            board_id: 게시판 ID
            original_ids: 조회할 original_post_id 리스트
            
        Returns:
            해당하는 게시물들의 목록
        """
        pass

    @abstractmethod
    async def update_posts_batch(self, posts: List[Post]) -> None:
        """여러 게시글을 배치로 업데이트합니다.
        
        Args:
            posts: 업데이트할 게시글 객체 리스트 (id 포함)
        """
        pass