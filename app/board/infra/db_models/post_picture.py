from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.db import Base


class PostPicture(Base):
    """게시글 사진 정보 DB 모델"""
    __tablename__ = "post_pictures"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="사진 ID")
    post_id = Column(Integer, ForeignKey("post.id"), nullable=False, comment="게시글 ID")
    url = Column(String(500), nullable=False, comment="사진 URL")
    picture_summary = Column(Text, nullable=False, comment="사진 요약/설명")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="생성 시간")
    
    # 관계 설정
    post = relationship("Post", back_populates="pictures")
