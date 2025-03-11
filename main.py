from fastapi import FastAPI
from routes.test_router import router
from contextlib import asynccontextmanager
from services.scheduler.scheduler import SchedulerService  # 우리가 만든 스케줄러 클래스
from services.board_scrapper.manager import BoardScraperManager
from services.board_scrapper.board_main import ExampleScraper1, ExampleScraper2

# 동기 작업 예시
def hello_scheduler():
    print("Hello, Scheduler!")

# ✅ 스케줄러 객체 생성 (전역 변수로 관리)
scheduler_service = SchedulerService()
board_manager = BoardScraperManager()
# scheduler_service.add_interval_job(hello_scheduler, 5)
# 실행할 함수만 직접 등록
scheduler_service.add_interval_job(board_manager.execute_next_scraper, seconds=5)

# 스크래퍼 추가
board_manager.add_scraper(ExampleScraper1())
board_manager.add_scraper(ExampleScraper2())

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

