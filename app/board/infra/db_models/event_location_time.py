from sqlalchemy import Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date, datetime, timezone
from .base import Base 

class EventLocationTime(Base):
    __tablename__ = "event_location_time"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey("post.id", ondelete="CASCADE"), nullable=False)
    location: Mapped[str | None] = mapped_column(String(500), nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True) 
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        default=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self) -> dict:
        """SQLAlchemy Model을 dict로 변환"""
        return {
            'id': self.id,
            'post_id': self.post_id,
            'location': self.location,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'created_at': self.created_at
        }