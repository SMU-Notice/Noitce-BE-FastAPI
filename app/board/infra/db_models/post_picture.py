from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.sql import func
from app.database.base import Base  # 공통 Base 사용

class PostPicture(Base):
    """게시글 사진 정보 DB 모델"""
    __tablename__ = "post_picture"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="사진 ID")
    post_id = Column(Integer, ForeignKey("post.id"), nullable=False, comment="게시글 ID")
    url = Column(String(500), nullable=False, comment="사진 URL")
    picture_summary = Column(Text, nullable=False, comment="사진 요약/설명")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="생성 시간")
    
    # ✅ 여기에 메서드 추가
    def to_pydantic_dict(self):
        """Pydantic 변환용 딕셔너리 (DB 쿼리 없음)"""
        return {
            'id': self.id,
            'post_id': self.post_id,
            'url': self.url,
            'picture_summary': self.picture_summary,
            'created_at': self.created_at
        }
    
