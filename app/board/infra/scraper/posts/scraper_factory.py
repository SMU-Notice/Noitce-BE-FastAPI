import logging
from typing import Dict, Optional
import os
from app.board.infra.scraper.posts.post_content_scraper import IPostContentScraper
from app.board.domain.post import Post
from app.board.infra.scraper.posts.main_board_post_scraper import MainBoardPostScraper

logger = logging.getLogger(__name__)

MAIN_BOARD_SANGMYUNG_BOARD_ID = int(os.getenv("MAIN_BOARD_SANGMYUNG_BOARD_ID"))
MAIN_BOARD_SEOUL_BOARD_ID = int(os.getenv("MAIN_BOARD_SEOUL_BOARD_ID"))

class PostScraperFactory:
    # board_id -> 스크래퍼 클래스 매핑
    _board_scraper_mapping: Dict[int, type] = {
        MAIN_BOARD_SANGMYUNG_BOARD_ID: MainBoardPostScraper,      
        MAIN_BOARD_SEOUL_BOARD_ID: MainBoardPostScraper,      
    }
    
    @classmethod
    def create_scraper_by_board_id(cls, post: Post) -> IPostContentScraper:
        """
        board_id에 따라 적절한 스크래퍼 생성
            
        Args:
            post (Post): 스크래핑할 게시물 정보 (board_id 포함)
                
        Returns:
            IPostContentScraper: board_id에 맞는 스크래퍼 인스턴스
                
        Raises:
            ValueError: 지원하지 않는 board_id인 경우
       """
        scraper_class = cls._board_scraper_mapping.get(post.board_id)


        if scraper_class:
            logger.info(f"스크래퍼 생성: {scraper_class.__name__} for board_id {post.board_id}")

            return scraper_class()
        else:
            raise ValueError(f"지원하지 않는 board_id: {post.board_id}")
        