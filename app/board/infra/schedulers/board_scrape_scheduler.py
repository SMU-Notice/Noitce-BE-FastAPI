import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging
from app.board.infra.scraper.board_scraper_base import BoardScraper
from app.board.application.scraped_post_manager import ScrapedPostManager
from app.board.infra.http_new_post_sender import HttpNewPostSender

logger = logging.getLogger(__name__)


class BoardScrapeScheduler:
    """게시판 스크래핑 작업을 스케줄링하는 클래스"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.scrape_lock = asyncio.Lock()
        self.scraped_post_manager = ScrapedPostManager(new_post_sender=HttpNewPostSender(webhook_endpoint="http://127.0.0.1:8080/api/board-subscription/new-posts"))

    def start(self):
        """스케줄러 시작"""
        self.scheduler.start()

    def stop(self):
        """스케줄러 종료"""
        self.scheduler.shutdown()

    def get_job_count(self) -> int:
        """등록된 작업 수 반환"""
        return len(self.scheduler.get_jobs())
    
    def add_board_scrape_job(self, scraper: BoardScraper):
        """
        주어진 BoardScraper 인스턴스를 일정한 주기로 실행하도록 스케줄링합니다.
        하나의 스크래핑 작업이 실행 중일 경우, 다른 작업은 scrape_lock을 통해 대기하도록 설정되어
        동시에 여러 스크래퍼가 실행되지 않도록 보장합니다.

        :param scraper: 주기적으로 실행될 게시판 스크래퍼 인스턴스. board_id 및 interval 속성이 포함되어야 함.
        """
        async def job():
            board_name = f"{scraper.__class__.__name__}_{getattr(scraper, 'board_id', 'unknown')}"

            # 스크래핑 작업이 이미 실행 중인 경우 대기
            if self.scrape_lock.locked():
                logger.info(f"[{board_name}] 스크랩 대기 중...")

            # 스크래핑 작업이 실행 중이지 않은 경우
            async with self.scrape_lock:
                logger.info(f"[{board_name}] 스크랩 시작")
                
                # 스크래퍼에서 raw 데이터 받기 (변환 없이)
                scraped_posts_dto = scraper.scrape()
                
                # Manager에게 raw 데이터 그대로 전달 (변환은 Manager에서 처리)
                await self.scraped_post_manager.manage_scraped_posts(scraped_posts_dto)
                
                logger.info(f"[{board_name}] 스크랩 완료")

        # 스크래퍼의 interval 속성에서 주기를 가져옴
        interval = getattr(scraper, 'interval', 3600)
        job_id = f"{scraper.__class__.__name__}_{getattr(scraper, 'board_id', 'unknown')}"

        # 스케줄러에 작업 추가
        self.scheduler.add_job(job, "interval", seconds=interval, id=job_id)
        logger.info(f"등록된 작업: {job_id} (interval={interval}s)")

    def remove_board_scrape_job(self, board_id: int):
        """게시판 스크래핑 작업 제거"""
        job_id = f"scrape_board_{board_id}"
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"게시판 스크래핑 작업 제거: {job_id}")
        except Exception as e:
            logger.warning(f"작업 제거 실패: {job_id}, {e}")