import asyncio
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging
from app.containers import Container
from dependency_injector.wiring import Provide, inject

from app.protest.infra.scraper.protest_scraper import ProtestScraper
from app.protest.application.protest_event_service import ProtestEventService

logger = logging.getLogger(__name__)


class ProtestScrapeScheduler:
    """시위 정보 스크래핑 작업을 특정 시각에 스케줄링하는 클래스"""
    
    @inject
    def __init__(   
        self,
        scheduler: AsyncIOScheduler = Provide[Container.scheduler],
        scrape_lock: asyncio.Lock = Provide[Container.scrape_lock],
        protest_service: ProtestEventService = Provide[Container.protest_service]
    ):
        self.scheduler = scheduler
        self.scrape_lock = scrape_lock
        self.protest_service = protest_service

    def start(self):
        """스케줄러 시작"""
        self.scheduler.start()

    def stop(self):
        """스케줄러 종료"""
        self.scheduler.shutdown()

    def get_job_count(self) -> int:
        """등록된 작업 수 반환"""
        return len(self.scheduler.get_jobs())
    
    def add_protest_scrape_job(self):
        """
        매일 환경변수에서 지정한 시각에 시위 정보를 스크래핑하도록 스케줄링합니다.
        기본값은 매일 오후 7시(19:00)입니다.
        
        환경변수: PROTEST_SCRAPE_HOUR, PROTEST_SCRAPE_MINUTE
        """
        # 환경변수에서 스케줄 시간 읽기
        hour = int(os.getenv("PROTEST_SCRAPE_HOUR", "19"))
        minute = int(os.getenv("PROTEST_SCRAPE_MINUTE", "0"))
        
        async def job():
            job_name = "ProtestScraper"

            # 스크래핑 작업이 이미 실행 중인 경우 대기
            if self.scrape_lock.locked():
                logger.info(f"[{job_name}] 스크랩 대기 중...")

            # 스크래핑 작업 실행
            async with self.scrape_lock:
                logger.info(f"[{job_name}] 시위 정보 스크랩 시작")
                
                try:
                    # 1. 스크래퍼로 데이터 수집
                    scraper = ProtestScraper()
                    raw_events = scraper.run()
                    
                    # 2. 서비스 층에 데이터 전달하여 비즈니스 로직 처리 (DB 저장 등)
                    await self.protest_service.save_protest_events(raw_events)
                    
                    logger.info(f"[{job_name}] 시위 정보 수집 및 저장 완료: {len(raw_events)}건")
                    
                except Exception as e:
                    logger.error(f"[{job_name}] 스크랩 실패: {e}")

        job_id = "protest_scraper_daily"

        # 매일 특정 시각에 실행하도록 cron 스케줄링
        self.scheduler.add_job(
            job, 
            "cron", 
            hour=hour, 
            minute=minute, 
            id=job_id
        )
    
        logger.info(f"등록된 작업: {job_id} (매일 {hour:02d}:{minute:02d})")

    def add_protest_scrape_job_with_cron(self, cron_expression: str, job_id: str = "protest_scraper_custom"):
        """
        Cron 표현식을 사용하여 유연한 스케줄링을 설정합니다.
        
        :param cron_expression: Cron 표현식 (예: "0 19 * * *" - 매일 19시)
        :param job_id: 작업 ID
        """
        async def job():
            job_name = f"ProtestScraper_{job_id}"

            if self.scrape_lock.locked():
                logger.info(f"[{job_name}] 스크랩 대기 중...")

            async with self.scrape_lock:
                logger.info(f"[{job_name}] 시위 정보 스크랩 시작")
                
                try:
                    # 1. 스크래퍼로 데이터 수집
                    scraper = ProtestScraper()
                    raw_events = scraper.run()
                    
                    # 2. 서비스 층에 데이터 전달하여 비즈니스 로직 처리 (DB 저장 등)
                    await self.protest_service.save_protest_events(raw_events)
                    
                    logger.info(f"[{job_name}] 시위 정보 수집 및 저장 완료: {len(raw_events)}건")
                    
                except Exception as e:
                    logger.error(f"[{job_name}] 스크랩 실패: {e}")

        # Cron 스케줄링
        self.scheduler.add_job(
            job,
            "cron",
            **self._parse_cron_expression(cron_expression),
            id=job_id
        )
        
        logger.info(f"등록된 작업: {job_id} (cron: {cron_expression})")

    def remove_protest_scrape_job(self, job_id: str = "protest_scraper_daily"):
        """시위 정보 스크래핑 작업 제거"""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"시위 스크래핑 작업 제거: {job_id}")
        except Exception as e:
            logger.warning(f"작업 제거 실패: {job_id}, {e}")

    def _parse_cron_expression(self, cron_expression: str) -> dict:
        """
        Cron 표현식을 APScheduler cron 파라미터로 변환
        예: "0 19 * * *" -> {"minute": 0, "hour": 19}
        """
        parts = cron_expression.split()
        if len(parts) != 5:
            raise ValueError("Cron 표현식은 5개 부분이어야 합니다 (분 시 일 월 요일)")
        
        minute, hour, day, month, day_of_week = parts
        
        cron_params = {}
        if minute != "*":
            cron_params["minute"] = minute
        if hour != "*":
            cron_params["hour"] = hour
        if day != "*":
            cron_params["day"] = day
        if month != "*":
            cron_params["month"] = month
        if day_of_week != "*":
            cron_params["day_of_week"] = day_of_week
            
        return cron_params