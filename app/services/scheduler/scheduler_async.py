import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from app.services.board_scrapper.scrapper_handler import handle_scraped_posts
from app.services.board_scrapper.base import BoardScraper
import logging

logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.scrape_lock = asyncio.Lock()
        # self.scheduler.add_listener(self._job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    def start(self):
        self.scheduler.start()

    def stop(self):
        self.scheduler.shutdown()

    def add_interval_job(self, func, seconds, *args, **kwargs):
        self.scheduler.add_job(func, "interval", seconds=seconds, args=args, kwargs=kwargs)

    def get_job_count(self):
        return len(self.scheduler.get_jobs())
    
    def add_scrape_job(self, scraper: BoardScraper):
        """
        주어진 BoardScraper 인스턴스를 일정한 주기로 실행하도록 스케줄링합니다.
        하나의 스크래핑 작업이 실행 중일 경우, 다른 작업은 scrape_lock을 통해 대기하도록 설정되어
        동시에 여러 스크래퍼가 실행되지 않도록 보장합니다.

        :param scraper: 주기적으로 실행될 게시판 스크래퍼 인스턴스. board_id 및 interval 속성이 포함되어야 함.
        """
        async def job():
            board_name = f"{scraper.__class__.__name__}_{getattr(scraper, 'board_id', 'unknown')}"
            logger.info(f"[{board_name}] 스크랩 대기 중...")
            async with self.scrape_lock:  # 락이 해제될 때까지 기다림
                logger.info(f"[{board_name}] 스크랩 시작")
                scraped = scraper.scrape()
                await handle_scraped_posts(scraped)
                logger.info(f"[{board_name}] 스크랩 완료")

        interval = getattr(scraper, 'interval', 3600)
        job_id = f"{scraper.__class__.__name__}_{getattr(scraper, 'board_id', 'unknown')}"

        self.scheduler.add_job(job, "interval", seconds=interval, id=job_id)
        logger.info(f"등록된 작업: {job_id} (interval={interval}s)")

    def _error_listener(self, event):
        print(f"[❌ 오류] {event.job_id}: {event.exception}")

    # ✅ 리스너 정의: 작업 완료시 handle_scraped_posts에 결과 전달
    def _job_listener(self, event):
        if event.exception:
            print(f"[❌ 작업 실패] {event.job_id}: {event.exception}")
        else:
            retval = event.retval
            print(f"[✅ 작업 성공] {event.job_id} 반환값: {retval}")
            asyncio.create_task(handle_scraped_posts(retval))


# 비동기 작업 예시
async def async_task():
    print(f"Hello, Scheduler! Time: {datetime.now()}")

