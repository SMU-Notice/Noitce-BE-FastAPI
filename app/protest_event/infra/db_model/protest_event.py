from datetime import date, time
from sqlalchemy import String, Integer, Date, Time
from sqlalchemy.orm import Mapped, mapped_column
from ....board.infra.db_models.base import Base 

class ProtestEvent(Base):
    __tablename__ = "protest_event"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    location: Mapped[str] = mapped_column("type", String(30), nullable=False)
    protest_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)