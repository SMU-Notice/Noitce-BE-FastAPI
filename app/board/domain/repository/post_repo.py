from abc import ABCMeta, abstractmethod
from typing import List
from app.board.domain.post import Post

class IPostRepository(metaclass=ABCMeta):
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