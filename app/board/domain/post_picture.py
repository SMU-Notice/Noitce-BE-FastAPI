from dataclasses import dataclass
from typing import Optional


@dataclass
class PostPicture:
    """게시글 사진 정보 도메인 객체"""
    url: str
    original_post_id: int                           
    picture_summary: Optional[str] = None               
    id: Optional[int] = None           
    post_id: Optional[int] = None      
    original_ocr_text: Optional[str] = None

    def to_dict(self) -> dict:
        """Domain Entity를 dict로 변환 (DB 저장용)"""
        return {
            'post_id': self.post_id,
            'url': self.url,
            'picture_summary': self.picture_summary,
            # id, created_at는 DB에서 자동 생성되므로 제외
            # original_post_id, original_ocr_text는 DB에 저장하지 않음
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PostPicture':
        """dict를 Domain Entity로 변환"""
        return cls(
            url=data.get('url'),
            original_post_id=data.get('original_post_id', 0),  # 기본값 추가
            picture_summary=data.get('picture_summary'),
            id=data.get('id'),
            post_id=data.get('post_id'),
            original_ocr_text=data.get('original_ocr_text'),
        )
