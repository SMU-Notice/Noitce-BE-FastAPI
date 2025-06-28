import aiohttp
import logging
from pydantic import BaseModel
from typing import Optional

# 로거 설정
logger = logging.getLogger(__name__)

# 보낼 메시지 구조 정의
class NewPosts(BaseModel):
   boardId: int
   post_types: Dict[str, List[int]]

class NewPostSender:
   def __init__(self, webhook_endpoint: str):
       self.webhook_endpoint = webhook_endpoint
   
   async def send_notification(self, new_posts_data: NewPosts):
       async with aiohttp.ClientSession() as session:
           # newPosts 키로 감싸서 전송
           payload = {"newPosts": new_posts_data.model_dump()}
           
           logger.info(f"Sending new posts notification to {self.webhook_endpoint}: {payload}")
           
           async with session.post(self.webhook_endpoint, json=payload) as response:
               if response.status == 200:
                   response_data = await response.json()
                   logger.info(f"New posts notification sent successfully! Response: {response_data}")
                   return response_data
               else:
                   error_text = await response.text()
                   logger.error(f"Failed to send new posts notification: {response.status}, Error: {error_text}")
                   return None