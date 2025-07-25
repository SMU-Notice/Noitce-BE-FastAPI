# app/board/domain/protest_event.py
from dataclasses import dataclass
from datetime import date, time
from typing import Optional

@dataclass
class ProtestEvent:
    location: str
    protest_date: date
    start_time: time
    end_time: time
    id: Optional[int] = None
    
    def to_dict(self):
        return {
            "id": self.id,
            "location": self.location,
            "protest_date": self.protest_date,
            "start_time": self.start_time,
            "end_time": self.end_time
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get("id"),
            location=data["location"],
            protest_date=data["protest_date"],
            start_time=data["start_time"],
            end_time=data["end_time"]
        )