from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Post(Base):
    __tablename__ = 'post'
    
    id = Column(Integer, primary_key=True, index=True)
    board_id = Column(Integer)  # ✅ board_id로 변경
    title = Column(String)
    summary = Column(Text)
    view_count = Column(Integer)
    url = Column(String)
    has_attachment = Column(Boolean, default=False)
    posted_date = Column(DateTime)

