import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.board.infra.schedulers.board_scrape_scheduler import BoardScrapeScheduler
from app.board.infra.schedulers.scraper_initializer import initialize_scrapers
from app.config.logging_config import setup_logging


# 로깅 설정
setup_logging()

logger = logging.getLogger(__name__)

# 스케줄러 객체 생성 
board_scheduler = BoardScrapeScheduler()


# 비동기 라이프사이클 관리
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting scheduler...")
    board_scheduler.start()  # 앱 시작 시 스케줄러 실행

    # 모든 스크래퍼 등록
    initialize_scrapers(board_scheduler)

    yield # 서버 실행

    logger.info("Shutting down scheduler...")
    board_scheduler.stop()  # 앱 종료 시 스케줄러 정리

# ✅ FastAPI 인스턴스 생성
app = FastAPI(lifespan=lifespan)

# 라우터 등록

# 기본 엔드포인트
@app.get("/")
async def read_root():
    logger.info("Welcome to FastAPI!")
    return {"message": "Welcome to FastAPI!"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "active_jobs": board_scheduler.get_job_count()
    }
