from dataclasses import dataclass
from typing import Optional
from app.board.domain.post import Post
from app.board.domain.event_location_time import EventLocationTime
from app.board.domain.post_picture import PostPicture


@dataclass
class SummaryProcessedPostDTO:
    """
    게시물 처리 결과를 담는 DTO 클래스
    Post, Location, PostPicture 엔티티를 모두 포함하며, Location과 PostPicture은 None이 올 수 있음
    """
    post: Post
    location: Optional[EventLocationTime] = None
    post_picture: Optional[PostPicture] = None  
    
    def __post_init__(self):
        """초기화 후 검증"""
        if not self.post:
            raise ValueError("post는 필수 필드입니다.")
    
    @classmethod
    def create_with_post_only(cls, post: Post) -> 'SummaryProcessedPostDTO':
        """
        Post만으로 SummaryProcessedPostDTO를 생성하는 팩토리 메서드
        
        Parameters:
        - post: 처리된 Post 객체
        
        Returns:
        - SummaryProcessedPostDTO: Post만 포함된 DTO
        """
        return cls(post=post)
    
    
    def has_location(self) -> bool:
        """위치 정보가 있는지 확인"""
        return self.location is not None
    
    def has_post_picture(self) -> bool:
        """PostPicture 정보가 있는지 확인"""
        return self.post_picture is not None
    
    def to_dict(self) -> dict:
        """딕셔너리 형태로 변환"""
        return {
            'post': self.post,
            'location': self.location.to_dict() if self.location else None,
            'post_picture': self.post_picture
        }
    
    def __repr__(self) -> str:
        return f"SummaryProcessedPostDTO(post_id={self.post.id}, has_location={self.has_location()}, has_post_picture={self.has_post_picture()})" 