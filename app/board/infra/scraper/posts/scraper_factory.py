import logging
from typing import Dict, Optional
import os
from app.board.infra.scraper.posts.post_content_scraper import IPostContentScraper
from app.board.domain.post import Post
from app.board.infra.scraper.posts.main_board_post_scraper import MainBoardPostScraper
from app.board.infra.scraper.posts.library_board_post_scraper import LibraryBoardPostScraper

logger = logging.getLogger(__name__)

# Board ID 환경변수 읽기
import os
from typing import Dict

# Board ID 환경변수 읽기
MAIN_BOARD_SANGMYUNG_BOARD_ID = int(os.getenv("MAIN_BOARD_SANGMYUNG_BOARD_ID"))
MAIN_BOARD_SEOUL_BOARD_ID = int(os.getenv("MAIN_BOARD_SEOUL_BOARD_ID"))
LIB_NOTICE_BOARD_ID = int(os.getenv("LIB_NOTICE_BOARD_ID"))
LIB_EDUBOARD_BOARD_ID = int(os.getenv("LIB_EDUBOARD_BOARD_ID"))
CS_NOTICE_BOARD_ID = int(os.getenv("CS_NOTICE_BOARD_ID"))
CS_SUGANG_BOARD_ID = int(os.getenv("CS_SUGANG_BOARD_ID"))
SLS_NOTICE_BOARD_ID = int(os.getenv("SLS_NOTICE_BOARD_ID"))
HISTORY_NOTICE_BOARD_ID = int(os.getenv("HISTORY_NOTICE_BOARD_ID"))
CC_NOTICE_BOARD_ID = int(os.getenv("CC_NOTICE_BOARD_ID"))
LIBINFO_NOTICE_BOARD_ID = int(os.getenv("LIBINFO_NOTICE_BOARD_ID"))
KJC_NOTICE_BOARD_ID = int(os.getenv("KJC_NOTICE_BOARD_ID"))
SPACE_NOTICE_BOARD_ID = int(os.getenv("SPACE_NOTICE_BOARD_ID"))
PUBLIC_NOTICE_BOARD_ID = int(os.getenv("PUBLIC_NOTICE_BOARD_ID"))
SMFAMILY_NOTICE_BOARD_ID = int(os.getenv("SMFAMILY_NOTICE_BOARD_ID"))
NS_NOTICE_BOARD_ID = int(os.getenv("NS_NOTICE_BOARD_ID"))
KOREDU_NOTICE_BOARD_ID = int(os.getenv("KOREDU_NOTICE_BOARD_ID"))
ENGEDU_NOTICE_BOARD_ID = int(os.getenv("ENGEDU_NOTICE_BOARD_ID"))
LEARNING_NOTICE_BOARD_ID = int(os.getenv("LEARNING_NOTICE_BOARD_ID"))
MATHED_NOTICE_BOARD_ID = int(os.getenv("MATHED_NOTICE_BOARD_ID"))
SMUBIZ_NOTICE_BOARD_ID = int(os.getenv("SMUBIZ_NOTICE_BOARD_ID"))
SBE_NOTICE_BOARD_ID = int(os.getenv("SBE_NOTICE_BOARD_ID"))
GBIZ_NOTICE_BOARD_ID = int(os.getenv("GBIZ_NOTICE_BOARD_ID"))
CM_NOTICE_BOARD_ID = int(os.getenv("CM_NOTICE_BOARD_ID"))
ELECTRIC_NOTICE_BOARD_ID = int(os.getenv("ELECTRIC_NOTICE_BOARD_ID"))
AIOT_NOTICE_BOARD_ID = int(os.getenv("AIOT_NOTICE_BOARD_ID"))
GAME_NOTICE_BOARD_ID = int(os.getenv("GAME_NOTICE_BOARD_ID"))
ANIMATION_NOTICE_BOARD_ID = int(os.getenv("ANIMATION_NOTICE_BOARD_ID"))
HI_NOTICE_BOARD_ID = int(os.getenv("HI_NOTICE_BOARD_ID"))
FBS_NOTICE_BOARD_ID = int(os.getenv("FBS_NOTICE_BOARD_ID"))
BIO_NOTICE_BOARD_ID = int(os.getenv("BIO_NOTICE_BOARD_ID"))
ICHEM_NOTICE_BOARD_ID = int(os.getenv("ICHEM_NOTICE_BOARD_ID"))
ENERGY_NOTICE_BOARD_ID = int(os.getenv("ENERGY_NOTICE_BOARD_ID"))
FOOD_NOTICE_BOARD_ID = int(os.getenv("FOOD_NOTICE_BOARD_ID"))
FASHION_NOTICE_BOARD_ID = int(os.getenv("FASHION_NOTICE_BOARD_ID"))
SPORTS_NOTICE_BOARD_ID = int(os.getenv("SPORTS_NOTICE_BOARD_ID"))
DANCE_NOTICE_BOARD_ID = int(os.getenv("DANCE_NOTICE_BOARD_ID"))
FINEARTS_NOTICE_BOARD_ID = int(os.getenv("FINEARTS_NOTICE_BOARD_ID"))
SMULAD_NOTICE_BOARD_ID = int(os.getenv("SMULAD_NOTICE_BOARD_ID"))
MUSIC_NOTICE_BOARD_ID = int(os.getenv("MUSIC_NOTICE_BOARD_ID"))
HAPPYDORM_NOTICE_BOARD_ID = int(os.getenv("HAPPYDORM_NOTICE_BOARD_ID"))
SMUDORM_NOTICE_BOARD_ID = int(os.getenv("SMUDORM_NOTICE_BOARD_ID"))
FOREIGN_NOTICE_BOARD_ID = int(os.getenv("FOREIGN_NOTICE_BOARD_ID"))
GRAD_NOTICE_BOARD_ID = int(os.getenv("GRAD_NOTICE_BOARD_ID"))
ICEE_NOTICE_BOARD_ID = int(os.getenv("ICEE_NOTICE_BOARD_ID"))
SWAI_NOTICE_BOARD_ID = int(os.getenv("SWAI_NOTICE_BOARD_ID"))
SMCAREER_NOTICE_BOARD_ID = int(os.getenv("SMCAREER_NOTICE_BOARD_ID"))

class PostScraperFactory:
    # board_id -> 스크래퍼 클래스 매핑
    _board_scraper_mapping: Dict[int, type] = {
        MAIN_BOARD_SANGMYUNG_BOARD_ID: MainBoardPostScraper,
        MAIN_BOARD_SEOUL_BOARD_ID: MainBoardPostScraper,
        LIB_NOTICE_BOARD_ID: LibraryBoardPostScraper,
        LIB_EDUBOARD_BOARD_ID: LibraryBoardPostScraper,
        CS_NOTICE_BOARD_ID: MainBoardPostScraper,
        CS_SUGANG_BOARD_ID: MainBoardPostScraper,
        SLS_NOTICE_BOARD_ID: MainBoardPostScraper,
        HISTORY_NOTICE_BOARD_ID: MainBoardPostScraper,
        CC_NOTICE_BOARD_ID: MainBoardPostScraper,
        LIBINFO_NOTICE_BOARD_ID: MainBoardPostScraper,
        KJC_NOTICE_BOARD_ID: MainBoardPostScraper,
        SPACE_NOTICE_BOARD_ID: MainBoardPostScraper,
        PUBLIC_NOTICE_BOARD_ID: MainBoardPostScraper,
        SMFAMILY_NOTICE_BOARD_ID: MainBoardPostScraper,
        NS_NOTICE_BOARD_ID: MainBoardPostScraper,
        KOREDU_NOTICE_BOARD_ID: MainBoardPostScraper,
        ENGEDU_NOTICE_BOARD_ID: MainBoardPostScraper,
        LEARNING_NOTICE_BOARD_ID: MainBoardPostScraper,
        MATHED_NOTICE_BOARD_ID: MainBoardPostScraper,
        SMUBIZ_NOTICE_BOARD_ID: MainBoardPostScraper,
        SBE_NOTICE_BOARD_ID: MainBoardPostScraper,
        GBIZ_NOTICE_BOARD_ID: MainBoardPostScraper,
        CM_NOTICE_BOARD_ID: MainBoardPostScraper,
        ELECTRIC_NOTICE_BOARD_ID: MainBoardPostScraper,
        AIOT_NOTICE_BOARD_ID: MainBoardPostScraper,
        GAME_NOTICE_BOARD_ID: MainBoardPostScraper,
        ANIMATION_NOTICE_BOARD_ID: MainBoardPostScraper,
        HI_NOTICE_BOARD_ID: MainBoardPostScraper,
        FBS_NOTICE_BOARD_ID: MainBoardPostScraper,
        BIO_NOTICE_BOARD_ID: MainBoardPostScraper,
        ICHEM_NOTICE_BOARD_ID: MainBoardPostScraper,
        ENERGY_NOTICE_BOARD_ID: MainBoardPostScraper,
        FOOD_NOTICE_BOARD_ID: MainBoardPostScraper,
        FASHION_NOTICE_BOARD_ID: MainBoardPostScraper,
        SPORTS_NOTICE_BOARD_ID: MainBoardPostScraper,
        DANCE_NOTICE_BOARD_ID: MainBoardPostScraper,
        FINEARTS_NOTICE_BOARD_ID: MainBoardPostScraper,
        SMULAD_NOTICE_BOARD_ID: MainBoardPostScraper,
        MUSIC_NOTICE_BOARD_ID: MainBoardPostScraper,
        HAPPYDORM_NOTICE_BOARD_ID: MainBoardPostScraper,
        SMUDORM_NOTICE_BOARD_ID: MainBoardPostScraper,
        FOREIGN_NOTICE_BOARD_ID: MainBoardPostScraper,
        GRAD_NOTICE_BOARD_ID: MainBoardPostScraper,
        ICEE_NOTICE_BOARD_ID: MainBoardPostScraper,
        SWAI_NOTICE_BOARD_ID: MainBoardPostScraper,
        SMCAREER_NOTICE_BOARD_ID: MainBoardPostScraper,
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
        