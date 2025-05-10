from fastapi import FastAPI
from app.routes.test_router import router
from contextlib import asynccontextmanager
# from services.scheduler.scheduler import SchedulerService  # 우리가 만든 스케줄러 클래스
from app.services.scheduler.scheduler_async import SchedulerService  # 비동기 스케줄러 클래스
from app.services.board_scrapper.scrapper_manager import BoardScraperManager
from app.services.board_scrapper import main_sangmyung, main_seoul

# 동기 작업 예시
def hello_scheduler():
    print("Hello, Scheduler!")

# ✅ 스케줄러 객체 생성 (전역 변수로 관리)
scheduler_service = SchedulerService()
board_manager = BoardScraperManager()

# 실행할 함수만 직접 등록
scheduler_service.add_interval_job(board_manager.execute_next_scraper, seconds=10)

# 스크래퍼 추가
board_manager.add_scraper(main_sangmyung.MainBoardSangmyungScraper())
board_manager.add_scraper(main_seoul.MainBoardSeoulScraper())

# 비동기 라이프사이클 관리
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting scheduler...")
    scheduler_service.start()  # 앱 시작 시 스케줄러 실행
    yield
    print("Shutting down scheduler...")
    scheduler_service.stop()  # 앱 종료 시 스케줄러 정리

# ✅ lifespan을 FastAPI에 적용
app = FastAPI(lifespan=lifespan)

# FastAPI 애플리케이션 생성 시 lifespan 이벤트 핸들러 사용
# app = FastAPI(lifespan=lifespan)
# app = FastAPI()


# 라우터 등록
app.include_router(router)

# 기본 엔드포인트
@app.get("/")
async def read_root():
    return {"message": "Welcome to FastAPI!"}

