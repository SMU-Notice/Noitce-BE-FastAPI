from apscheduler.schedulers.background import BackgroundScheduler
from typing import Callable, List

class SchedulerService:
    def __init__(self) -> None:
        # BackgroundScheduler 객체 초기화
        self.scheduler = BackgroundScheduler()

    def start(self) -> None:
        """스케줄러 시작"""
        self.scheduler.start()

    def stop(self) -> None:
        """스케줄러 종료"""
        self.scheduler.shutdown()

    def add_interval_job(self, func: Callable, seconds: int, *args: tuple, **kwargs: dict) -> None:
        """
        주기적인 작업을 스케줄에 추가.
        :param func: 실행할 함수
        :param seconds: 간격(초)
        :param args: 함수에 전달할 위치 인수들
        :param kwargs: 함수에 전달할 키워드 인수들
        """
        self.scheduler.add_job(func, "interval", seconds=seconds, args=args, kwargs=kwargs)

    def get_job_count(self) -> int:
        """
        현재 스케줄러에 등록된 작업의 수를 반환.
        :return: 등록된 작업의 수
        """
        return len(self.scheduler.get_jobs())



# 사용 예시
if __name__ == "__main__":
    scheduler_service = SchedulerService()
    scheduler_service.add_interval_job(lambda: print("Hello, Scheduler!"), 5)
    scheduler_service.start()
