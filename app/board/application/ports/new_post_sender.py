from app.board.application.dto.new_post_notification import NewPostNotificationDTO
from abc import ABC, abstractmethod
from typing import Optional

# 서비스 층 인터페이스
class INewPostSender(ABC):
    """새 게시물 전송 인터페이스"""
    
    @abstractmethod
    async def send_notification(self, new_posts_data: NewPostNotificationDTO) -> Optional[dict]:
        """
        새 게시물을 외부 시스템에 전송
        
        Args:
            new_posts_data: 전송할 새 게시물 데이터
            
        Returns:
            Optional[dict]: 성공 시 응답 데이터, 실패 시 None
        """
        pass