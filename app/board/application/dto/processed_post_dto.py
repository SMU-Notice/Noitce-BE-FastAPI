from dataclasses import dataclass
from typing import Optional
from app.board.domain.post import Post
from app.board.domain.event_location_time import EventLocationTime


@dataclass
class ProcessedPostDTO:
    """
    게시물 처리 결과를 담는 DTO 클래스
    Post, Location, OCR 엔티티를 모두 포함하며, Location과 OCR은 None이 올 수 있음
    """
    post: Post
    location: Optional[EventLocationTime] = None
    ocr_entity: Optional[dict] = None  # OCR 엔티티가 아직 구현되지 않아 dict로 임시 설정
    
    def __post_init__(self):
        """초기화 후 검증"""
        if not self.post:
            raise ValueError("post는 필수 필드입니다.")
    
    @classmethod
    def create_with_post_only(cls, post: Post) -> 'ProcessedPostDTO':
        """
        Post만으로 ProcessedPostDTO를 생성하는 팩토리 메서드
        
        Parameters:
        - post: 처리된 Post 객체
        
        Returns:
        - ProcessedPostDTO: Post만 포함된 DTO
        """
        return cls(post=post)
    
    @classmethod
    def create_with_location(cls, post: Post, location: EventLocationTime) -> 'ProcessedPostDTO':
        """
        Post와 Location으로 ProcessedPostDTO를 생성하는 팩토리 메서드
        
        Parameters:
        - post: 처리된 Post 객체
        - location: 추출된 위치 정보
        
        Returns:
        - ProcessedPostDTO: Post와 Location을 포함한 DTO
        """
        return cls(post=post, location=location)
    
    @classmethod
    def create_with_ocr(cls, post: Post, ocr_entity: dict) -> 'ProcessedPostDTO':
        """
        Post와 OCR으로 ProcessedPostDTO를 생성하는 팩토리 메서드
        
        Parameters:
        - post: 처리된 Post 객체
        - ocr_entity: OCR 처리 결과
        
        Returns:
        - ProcessedPostDTO: Post와 OCR을 포함한 DTO
        """
        return cls(post=post, ocr_entity=ocr_entity)
    
    @classmethod
    def create_complete(cls, post: Post, location: Optional[EventLocationTime] = None, ocr_entity: Optional[dict] = None) -> 'ProcessedPostDTO':
        """
        모든 정보로 ProcessedPostDTO를 생성하는 팩토리 메서드
        
        Parameters:
        - post: 처리된 Post 객체
        - location: 추출된 위치 정보 (선택사항)
        - ocr_entity: OCR 처리 결과 (선택사항)
        
        Returns:
        - ProcessedPostDTO: 모든 정보를 포함한 DTO
        """
        return cls(post=post, location=location, ocr_entity=ocr_entity)
    
    def has_location(self) -> bool:
        """위치 정보가 있는지 확인"""
        return self.location is not None
    
    def has_ocr(self) -> bool:
        """OCR 정보가 있는지 확인"""
        return self.ocr_entity is not None
    
    def to_dict(self) -> dict:
        """딕셔너리 형태로 변환"""
        return {
            'post': self.post,
            'location': self.location.to_dict() if self.location else None,
            'ocr_entity': self.ocr_entity
        }
    
    def __repr__(self) -> str:
        return f"ProcessedPostDTO(post_id={self.post.id}, has_location={self.has_location()}, has_ocr={self.has_ocr()})" 