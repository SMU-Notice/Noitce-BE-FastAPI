import logging
from fastapi import FastAPI
from app.routes.test_router import router
from contextlib import asynccontextmanager
# from app.services.scheduler.scheduler_async import SchedulerService  # 비동기 스케줄러 클래스
# from app.services.board_scrapper.main_board_scraper import MainBoardScraper
from app.board.infra.schedulers.board_scrape_scheduler import BoardScrapeScheduler
from app.board.infra.scraper.main_board_scraper import MainBoardScraper
from app.board.infra.schedulers.scraper_initializer import initialize_scrapers



# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()  # 콘솔 출력,
    ],
    force=True
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 동기 작업 예시
def hello_scheduler():
    logger.info("Hello, Scheduler!")

# ✅ 스케줄러 객체 생성 (전역 변수로 관리)
board_scheduler = BoardScrapeScheduler()


# board_manager.add_scraper(main_board_scraper.MainBoardScraper(campus_filter="sang", board_id=1))
# board_manager.add_scraper(main_board_scraper.MainBoardScraper(campus_filter="seoul", board_id=2))


# 비동기 라이프사이클 관리
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting scheduler...")
    board_scheduler .start()  # 앱 시작 시 스케줄러 실행

    # 모든 스크래퍼 등록
    initialize_scrapers(board_scheduler)

    yield # 서버 실행


    logger.info("Shutting down scheduler...")
    board_scheduler.stop()  # 앱 종료 시 스케줄러 정리

# ✅ FastAPI 인스턴스 생성
app = FastAPI(lifespan=lifespan)

# 라우터 등록
app.include_router(router)

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
