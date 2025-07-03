from typing import Optional
import aiohttp
import logging
from app.board.application.interfaces.new_post_sender import INewPostSender
from app.board.application.dto.new_post_notification import NewPostNotificationDTO

# 로거 설정
logger = logging.getLogger(__name__)

class HttpNewPostSender(INewPostSender):
    """HTTP 웹훅을 통한 새 게시물 전송 구현체"""
    
    def __init__(self, webhook_endpoint: str):
        self.webhook_endpoint = webhook_endpoint
    
    async def send_notification(self, new_posts_data: NewPostNotificationDTO) -> Optional[dict]:
        """
        HTTP 웹훅으로 새 게시물 알림 전송
        
        Args:
            new_posts_data: 전송할 새 게시물 데이터
            
        Returns:
            Optional[dict]: 성공 시 응답 데이터, 실패 시 None
        """
        async with aiohttp.ClientSession() as session:
            try:
                # newPosts 키로 감싸서 전송 (camelCase 변환)
                payload = new_posts_data.model_dump(by_alias=True)
                
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
                        
            except aiohttp.ClientError as e:
                logger.error(f"HTTP client error while sending notification: {e}")
                return None
            except Exception as e:
                logger.error(f"Unexpected error while sending notification: {e}")
                return None
