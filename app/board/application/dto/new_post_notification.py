from typing import Dict, List
from pydantic import BaseModel, Field

class NewPostNotificationDTO(BaseModel):
    board_id: int = Field(alias='boardId')
    post_types: Dict[str, List[int]] = Field(alias='postTypes')
    
    class Config:
        populate_by_name = True 