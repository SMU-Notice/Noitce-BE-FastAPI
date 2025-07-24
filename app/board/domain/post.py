from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional

@dataclass
class Post:
    board_id: int
    original_post_id: int
    post_type: str
    title: str
    url: str
    posted_date: date
    view_count: int
    has_reference: bool
    id: Optional[int] = None
    content_summary: Optional[str] = "N/A"
