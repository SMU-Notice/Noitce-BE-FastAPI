from sqlalchemy import Column, BigInteger, String, Integer, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class MainNoticeBoard(Base):
    __tablename__ = "main_notice_board"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    article_id = Column(BigInteger, unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    date = Column(DateTime, nullable=False)
    campus = Column(String(100))
    category = Column(String(100))
    views = Column(Integer, default=0)
    url = Column(Text, nullable=False)
    created_at = Column(DateTime)  # 데이터베이스에서 기본 생성
