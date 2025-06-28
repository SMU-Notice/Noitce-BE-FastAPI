from dataclasses import dataclass
from typing import List, Any


@dataclass
class ClassificationResult:
    """
    게시물 분류 결과를 담는 DTO 클래스
    """
    new_posts: List[Any] = None
    existing_posts_updates: List[Any] = None
    
    def __post_init__(self):
        if self.new_posts is None:
            self.new_posts = []
        if self.existing_posts_updates is None:
            self.existing_posts_updates = []
    
    @property
    def has_new_posts(self) -> bool:
        """신규 게시물이 있는지 확인"""
        return len(self.new_posts) > 0
    
    @property
    def has_existing_posts(self) -> bool:
        """기존 게시물 업데이트가 있는지 확인"""
        return len(self.existing_posts_updates) > 0