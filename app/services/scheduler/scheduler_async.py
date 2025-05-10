import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

class SchedulerService:
    def __init__(self):
        # 비동기 스케줄러 사용
        self.scheduler = AsyncIOScheduler()

    def start(self):
        # 이미 실행 중인 이벤트 루프에서 스케줄러를 시작
        self.scheduler.start()

    def stop(self):
        self.scheduler.shutdown()

    def add_interval_job(self, func, seconds, *args, **kwargs):
        # 비동기 함수 작업을 interval 방식으로 등록
        self.scheduler.add_job(func, "interval", seconds=seconds, args=args, kwargs=kwargs)

    def get_job_count(self):
        return len(self.scheduler.get_jobs())

# 비동기 작업 예시
async def async_task():
    print(f"Hello, Scheduler! Time: {datetime.now()}")

