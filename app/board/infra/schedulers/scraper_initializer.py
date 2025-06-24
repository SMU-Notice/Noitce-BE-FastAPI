# app/board/infra/schedulers/scraper_initializer.py
import logging
from app.board.infra.scraper.main_board_scraper import MainBoardScraper
from app.board.infra.schedulers.board_scrape_scheduler import BoardScrapeScheduler

logger = logging.getLogger(__name__)

def initialize_scrapers(scheduler: BoardScrapeScheduler):
    """모든 스크래퍼를 한번에 등록"""
    logger.info("스크래퍼 등록 시작")
    
    # 등록할 스크래퍼 목록 정의
    scrapers = [
        MainBoardScraper("main_board_sangmyung"),  # 상명 캠퍼스
        MainBoardScraper("main_board_seoul"),      # 서울 캠퍼스
        # 새로운 스크래퍼 추가 시 여기에 추가
        # NewBoardScraper("new_config"),
    ]
    
    # 일괄 등록
    for scraper in scrapers:
        scheduler.add_board_scrape_job(scraper)
        scraper_name = f"{scraper.__class__.__name__}_{getattr(scraper, 'board_id', 'unknown')}"
        logger.info(f"{scraper_name} 등록 완료")
    
    logger.info(f"모든 스크래퍼 등록 완료: 총 {len(scrapers)}개")