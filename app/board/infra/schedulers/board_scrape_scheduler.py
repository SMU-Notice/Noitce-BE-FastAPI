# domains/board/infrastructure/schedulers/BoardScrapeScheduler.py
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import logging
from typing import Callable, List, Dict, Any
from app.board.infra.scraper.board_scraper_base import BoardScraper
from app.board.domain.post import Post
from app.board.infra.scraper.models.scraped_post import ScrapedPost
from app.board.application.scrape_board_handler import ScrapedPostHandler

logger = logging.getLogger(__name__)

def scraped_post_to_domain(scraped: ScrapedPost, board_id: int) -> Post:
    return Post(
        board_id=board_id,
        original_post_id=int(scraped.original_post_id),
        post_type=scraped.post_type,
        title=scraped.title,
        url=scraped.url,
        posted_date=datetime.strptime(scraped.date, "%Y-%m-%d").date(),  # 날짜 포맷에 맞게 수정
        view_count=int(scraped.view_count),
        has_reference=scraped.has_reference
    )

class BoardScrapeScheduler:
    """게시판 스크래핑 작업을 스케줄링하는 클래스"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.scrape_lock = asyncio.Lock()
        self.scraped_post_handler = ScrapedPostHandler()

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
                scraped_posts_dto = scraper.scrape()
                
                # dict 구조를 유지하면서 값만 Post로 변환
                converted_data = {
                    original_post_id: scraped_post_to_domain(scraped_post, scraper.board_id)
                    for original_post_id, scraped_post in scraped_posts_dto["data"].items()
                }
                
                # data를 변환된 dict로 교체
                scraped_posts_dto["data"] = converted_data
                
                await self.scraped_post_handler.handleScrapedPosts(scraped_posts_dto)
                logger.info(f"[{board_name}] 스크랩 완료")

        # 스크래퍼의 interval 속성에서 주기를 가져옴
        interval = getattr(scraper, 'interval', 3600)
        job_id = f"{scraper.__class__.__name__}_{getattr(scraper, 'board_id', 'unknown')}"

        # 스케줄러에 작업 추가
        self.scheduler.add_job(job, "interval", seconds=interval, id=job_id)
        logger.info(f"등록된 작업: {job_id} (interval={interval}s)")

    # def get_running_jobs_info(self) -> List[Dict[str, Any]]:
    #     """현재 실행 중인 작업들의 board_id와 job_id 반환"""
    #     running_jobs_info = []
        
    #     # 실행 중인 작업들 가져오기
    #     running_jobs = self.scheduler.get_running_jobs()
        
    #     for job in running_jobs:
    #         job_info = {
    #             "job_id": job.id,
    #             "board_id": None
    #         }
            
    #         # job_id에서 board_id 추출 (예: "scrape_board_1" -> 1)
    #         if job.id and job.id.startswith("scrape_board_"):
    #             try:
    #                 board_id_str = job.id.split("scrape_board_")[1]
    #                 job_info["board_id"] = int(board_id_str)
    #             except (IndexError, ValueError):
    #                 pass
            
    #         # SCRAPER_CONFIGS의 키와 매칭 (예: "main_board_sangmyung")
    #         # job_id가 "scrape_board_1"이면 SCRAPER_CONFIGS에서 board_id=1인 항목 찾기
    #         if job_info["board_id"]:
    #             for config_name, config in SCRAPER_CONFIGS.items():
    #                 if config.board_id == job_info["board_id"]:
    #                     job_info["config_name"] = config_name
    #                     break
            
    #         running_jobs_info.append(job_info)
        
    #     return running_jobs_info

    def remove_board_scrape_job(self, board_id: int):
        """게시판 스크래핑 작업 제거"""
        job_id = f"scrape_board_{board_id}"
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"게시판 스크래핑 작업 제거: {job_id}")
        except Exception as e:
            logger.warning(f"작업 제거 실패: {job_id}, {e}")