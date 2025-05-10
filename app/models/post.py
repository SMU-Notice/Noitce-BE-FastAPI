from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, Date, DateTime, func
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()

class Board(Base):
    __tablename__ = "board"

    id = Column(Integer, primary_key=True, autoincrement=True)
    campus = Column(Enum("sangmyung", "seoul", name="campus_enum"), nullable=False)
    site = Column(String(255), nullable=False)
    board_type = Column(String(255), nullable=False)
    url = Column(Text, nullable=False)



class Post(Base):
    __tablename__ = "post"

    id = Column(Integer, primary_key=True, autoincrement=True)
    board_id = Column(Integer, ForeignKey("board.id", ondelete="CASCADE"), nullable=False)
    original_post_id = Column(Integer, nullable=False)
    type_ = Column("type",String(30), nullable=False)
    title = Column(String(255), nullable=False)
    content_summary = Column(Text, nullable=True)
    view_count = Column(Integer, nullable=False, default=0)
    url = Column(Text, nullable=False)
    has_reference = Column(Boolean, nullable=False, default=False)
    posted_date = Column(Date, nullable=False)
    scraped_at = Column(DateTime, server_default=func.current_timestamp())
