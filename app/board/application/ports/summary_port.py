from abc import ABC, abstractmethod

class SummaryPort(ABC):
    """요약 서비스 아웃바운드 포트"""
    
    @abstractmethod
    async def summarize_post_content(self, content: str) -> str:
        """
        게시물 본문을 요약합니다.
        
        Args:
            content: 요약할 게시물 본문
            
        Returns:
            요약된 텍스트
        """
        pass