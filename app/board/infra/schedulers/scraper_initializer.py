# app/board/infra/schedulers/scraper_initializer.py
import logging
from app.board.infra.scraper.boards.main_board_scraper import MainBoardScraper
from app.board.infra.scraper.boards.library_board_scraper import LibraryBoardScraper

from app.board.infra.scraper.boards.major_board_scraper import MajorBoardScraper

from app.board.infra.scraper.boards.additional_board_scraper import AdditionalBoardScraper

from app.board.infra.scraper.boards.swai_board_scraper import SwaiBoardScraper

from app.board.infra.scraper.boards.smcareer_board_scraper import SmCareerBoardScraper
from app.board.infra.schedulers.board_scrape_scheduler import BoardScrapeScheduler

logger = logging.getLogger(__name__)

def initialize_scrapers(scheduler: BoardScrapeScheduler):
    """모든 스크래퍼를 한번에 등록"""
    logger.info("스크래퍼 등록 시작")
    
    # 등록할 스크래퍼 목록 정의
    scrapers = [
        MainBoardScraper("main_board_sangmyung"),  # 상명 캠퍼스
        MainBoardScraper("main_board_seoul"),      # 서울 캠퍼스
        LibraryBoardScraper("lib_notice"),     # 학술정보관 공지사항
        LibraryBoardScraper("lib_eduboard"),   # 학술정보관 교육공지


        MajorBoardScraper("cs_notice"),   # 컴퓨터과학전공 공지사항
        MajorBoardScraper("cs_sugang"),   # 컴퓨터과학전공 수강신청
        MajorBoardScraper("sls_notice"),   
        MajorBoardScraper("history_notice"), 
        MajorBoardScraper("cc_notice"), 
        MajorBoardScraper("libinfo_notice"), 
        MajorBoardScraper("kjc_notice"), 
        MajorBoardScraper("space_notice"), 
        MajorBoardScraper("public_notice"), 
        MajorBoardScraper("smfamily_notice"), 
        MajorBoardScraper("ns_notice"), 
        MajorBoardScraper("koredu_notice"),        # 국어교육과
        MajorBoardScraper("engedu_notice"),        # 영어교육과
        MajorBoardScraper("learning_notice"),      # 교육학과
        MajorBoardScraper("mathed_notice"),        # 수학교육과
        MajorBoardScraper("smubiz_notice"),        # 경영학부
        MajorBoardScraper("sbe_notice"),           # 경제금융학부
        MajorBoardScraper("gbiz_notice"),          # 글로벌경영학과
        MajorBoardScraper("cm_notice"),            # 융합경영학과
        MajorBoardScraper("electric_notice"),      # 전기공학전공
        MajorBoardScraper("aiot_notice"),          # 지능IOT융합전공
        MajorBoardScraper("game_notice"),          # 게임전공
        MajorBoardScraper("animation_notice"),     # 애니메이션전공
        MajorBoardScraper("hi_notice"),            # 휴먼지능정보공학전공
        MajorBoardScraper("fbs_notice"),           # 핀테크빅데이터융합스마트생산전공
        MajorBoardScraper("bio_notice"),           # 생명공학전공
        MajorBoardScraper("ichem_notice"),         # 화공신소재전공
        MajorBoardScraper("energy_notice"),        # 화학에너지공학전공
        MajorBoardScraper("food_notice"),          # 식품영양학전공
        MajorBoardScraper("fashion_notice"),       # 의류학전공
        MajorBoardScraper("sports_notice"),        # 스포츠건강관리전공
        MajorBoardScraper("dance_notice"),         # 무용예술전공
        MajorBoardScraper("finearts_notice"),      # 조형예술전공
        MajorBoardScraper("smulad_notice"),        # 무형예술전공
        MajorBoardScraper("music_notice"),         # 음악학부

        AdditionalBoardScraper("happydorm_notice"),
        AdditionalBoardScraper("smudorm_notice"),

        AdditionalBoardScraper("foreign_notice"),

        AdditionalBoardScraper("grad_notice"),

        AdditionalBoardScraper("icee_notice"),

        SwaiBoardScraper("swai_notice"),

        SmCareerBoardScraper("sm_career"),
        # 새로운 스크래퍼 추가 시 여기에 추가
        # NewBoardScraper("new_config"),
    ]
    
    # 일괄 등록
    for scraper in scrapers:
        scheduler.add_board_scrape_job(scraper)
        scraper_name = f"{scraper.__class__.__name__}_{getattr(scraper, 'board_id', 'unknown')}"
        logger.info(f"{scraper_name} 등록 완료")
    
    logger.info(f"모든 스크래퍼 등록 완료: 총 {len(scrapers)}개")