from abc import ABC, abstractmethod
from app.board.domain.post import Post
from app.board.application.dto.scraped_content import ScrapedContent


# PostContentScraperPort 인터페이스
class PostContentScraperPort(ABC):
    
    @abstractmethod
    def extract_post_from_url(self, post: Post) -> ScrapedContent:
        """
        URL에서 게시물 내용을 추출하는 메서드
        
        Args:
            Post: 추출할 게시물 Post 객체
            
        Returns:
            ScrapedContent: 추출된 텍스트와 이미지 URL 리스트
        """
        pass