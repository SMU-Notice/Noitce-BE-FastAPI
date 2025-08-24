# app/board/infra/db_models/board.py
from sqlalchemy import String, Text, Integer, Enum
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base  # 공통 Base 사용

class Board(Base):
    __tablename__ = "board"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    campus: Mapped[str] = mapped_column(Enum("sangmyung", "seoul", name="campus_enum"), nullable=False)
    site: Mapped[str] = mapped_column(String(255), nullable=False)
    board_type: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)