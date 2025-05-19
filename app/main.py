import logging
from fastapi import FastAPI
from app.routes.test_router import router
from contextlib import asynccontextmanager
# from services.scheduler.scheduler import SchedulerService  # 우리가 만든 스케줄러 클래스
from app.services.scheduler.scheduler_async import SchedulerService  # 비동기 스케줄러 클래스
from app.services.board_scrapper.scrapper_manager import BoardScraperManager
from app.services.board_scrapper.main_board_scraper import MainBoardScraper




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
scheduler_service = SchedulerService()
# board_manager = BoardScraperManager()

# # 실행할 함수만 직접 등록
# scheduler_service.add_interval_job(board_manager.execute_next_scraper, seconds=10)


# board_manager.add_scraper(main_board_scraper.MainBoardScraper(campus_filter="sang", board_id=1))
# board_manager.add_scraper(main_board_scraper.MainBoardScraper(campus_filter="seoul", board_id=2))

# 상명 캠퍼스 크롤러 등록
sang_scraper = MainBoardScraper(campus_filter="sang", board_id=1)
scheduler_service.add_scrape_job(sang_scraper)

# 서울 캠퍼스 크롤러 등록
seoul_scraper = MainBoardScraper(campus_filter="seoul", board_id=2)
scheduler_service.add_scrape_job(seoul_scraper)

# 비동기 라이프사이클 관리
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting scheduler...")
    scheduler_service.start()  # 앱 시작 시 스케줄러 실행
    yield
    logger.info("Shutting down scheduler...")
    scheduler_service.stop()  # 앱 종료 시 스ddw케줄러 정리

# ✅ FastAPI 인스턴스 생성
app = FastAPI(lifespan=lifespan)

# 라우터 등록
app.include_router(router)

# 기본 엔드포인트
@app.get("/")
async def read_root():
    logger.info("Welcome to FastAPI!")
    return {"message": "Welcome to FastAPI!"}
