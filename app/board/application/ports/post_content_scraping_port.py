from abc import ABC, abstractmethod
from app.board.domain.post import Post
from app.board.application.dto.processed_post_dto import ProcessedPostDTO


# PostContentScraperPort 인터페이스
class PostContentScraperPort(ABC):
    
    @abstractmethod
    async def extract_post_from_url(self, post: Post) -> ProcessedPostDTO:
        """
        URL에서 게시물 내용을 추출하는 메서드
        
        Args:
            post: 추출할 게시물 Post 객체
            
        Returns:
            ProcessedPostDTO: Post, Location, OCR 엔티티를 포함한 처리 결과
        """
        pass