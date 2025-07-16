import logging
from typing import List
from sqlalchemy.exc import SQLAlchemyError
from app.board.infra.repository.post_repo import PostRepository
from app.board.domain.post import Post as PostVO
from app.board.application.ports.post_content_scraping_port import PostContentScraperPort
from app.board.infra.scraper.posts.web_post_content_scraper import WebPostContentScraper


logger = logging.getLogger(__name__)


class NewPostHandler:
    """새로운 게시물 처리 전용 클래스"""
    
    def __init__(self, post_repo: PostRepository = None, content_scraper: PostContentScraperPort = None):
        self.post_repo = post_repo or PostRepository()
        self.content_scraper = content_scraper or WebPostContentScraper()
    
    async def handle_new_posts(self, new_posts: List[PostVO]) -> List[PostVO]:
        """
        새로운 게시물들을 처리 (저장) 후 저장된 데이터 반환
        
        Parameters:
        - new_posts: 저장할 신규 PostVO 객체 목록
        
        Returns:
        - List[PostVO]: 저장된 게시물 객체 목록 (ID 등 DB에서 생성된 값 포함)
        """
        processed_posts = []
        
        for post in new_posts:
            logger.info("NewPostHandler: 신규 게시물 처리 시작 (게시물 이름): %s", post.title)

                # 필요시 게시물 전처리 작업 수행
                # 예: 데이터 검증, 변환 등
            if not post.title or not post.url:
                logger.warning("필수 필드 누락된 게시물 스킵: %s", post)
                continue

            try:
                processed_post: PostVO = await self.content_scraper.extract_post_from_url(post)
                logger.info("게시물 내용 추출 완료: %s", processed_post.title)
            
            except Exception as e:
                logger.error("게시물 내용 추출 중 오류 발생: %s - %s", post.title, e)
                continue

            processed_posts.append(processed_post)
                    

        try:
            saved_posts = await self.post_repo.create_posts(new_posts)
            logger.info("NewPostHandler: %d개 신규 게시물 저장 완료", len(saved_posts))
            return saved_posts
        except SQLAlchemyError as e:
            logger.error("NewPostHandler: 저장 실패: %s", e)
            raise