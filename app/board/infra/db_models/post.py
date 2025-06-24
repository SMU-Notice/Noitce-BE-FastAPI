from datetime import datetime, date, timezone
from sqlalchemy import String, Text, Integer, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
from .base import Base 

class Post(Base):
    __tablename__ = "post"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    board_id: Mapped[int] = mapped_column(Integer, ForeignKey("board.id", ondelete="CASCADE"), nullable=False)
    original_post_id: Mapped[int] = mapped_column(Integer, nullable=False)
    type_: Mapped[str] = mapped_column("type", String(30), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    view_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    has_reference: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    posted_date: Mapped[date] = mapped_column(Date, nullable=False)
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        default=lambda: datetime.now(timezone.utc)
    )