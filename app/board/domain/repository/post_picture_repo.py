from abc import ABC, abstractmethod
from app.board.domain.post_picture import PostPicture


class IPostPictureRepository(ABC):
    """PostPicture Repository Interface"""
    
    @abstractmethod
    async def create_post_picture(self, picture: PostPicture) -> PostPicture:
        """
        게시글 사진 정보를 저장합니다.
        
        Args:
            picture (PostPicture): 저장할 게시글 사진 도메인 객체
            
        Returns:
            PostPicture: 저장된 게시글 사진 객체 (DB에서 생성된 ID 등 포함)
        """
        pass