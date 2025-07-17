from pydantic import BaseModel
from typing import List, Optional

class ScrapedContent(BaseModel):
    text: Optional[str] = None
    image_urls: Optional[List[str]] = None