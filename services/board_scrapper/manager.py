from abc import ABC, abstractmethod
from apscheduler.schedulers.background import BackgroundScheduler
from collections import deque # 단일 스레드에서 사용 예정
from services.board_scrapper.base import BoardScraper

class BoardScraperManager:
    def __init__(self):
        self.scraper_queue = deque()  # deque 사용

    def add_scraper(self, scraper: BoardScraper):
        """새로운 스크래퍼를 큐에 추가"""
        self.scraper_queue.append(scraper)  # deque에 항목 추가


    def execute_next_scraper(self):
            """큐에서 제일 앞에 있는 스크래퍼 실행 후 다시 큐 뒤로 보냄"""
            if self.scraper_queue:
                scraper = self.scraper_queue.popleft()  # deque에서 맨 앞의 스크래퍼 가져옴
                print(f"실행 중: {scraper.__class__.__name__}")
                scraped_data = scraper.scrape()  # 스크래퍼 실행하고 반환값 받기

                # 데이터베이스에 저장
                # self.db_service.save_scraped_data(scraped_data)

                # 메시지 전송 (예시: 로그 출력)
                # print(f"데이터 저장 완료: {scraped_data}")

                self.scraper_queue.append(scraper)  # 다시 큐 뒤로 보냄


