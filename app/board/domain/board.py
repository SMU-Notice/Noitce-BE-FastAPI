from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Board:
    id: Optional[int] = None
    campus: str
    site: str
    board_type: str
    url: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)