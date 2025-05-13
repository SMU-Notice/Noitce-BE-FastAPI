from collections import deque # 단일 스레드에서 사용 예정
from app.services.board_scrapper.base import BoardScraper
from app.services.board_scrapper.scrapper_handler import handle_scraped_posts

## 전략 패턴 

class BoardScraperManager:
    def __init__(self):
        self.scraper_queue = deque()  

    def add_scraper(self, scraper: BoardScraper):
        """
        새로운 스크래퍼를 큐에 추가
        """
        self.scraper_queue.append(scraper)


    async def execute_next_scraper(self):
            """
            큐에서 제일 앞에 있는 스크래퍼 실행 후 다시 큐 뒤로 보냄
            """
            if self.scraper_queue:
                scraper = self.scraper_queue.popleft()  # deque에서 맨 앞의 스크래퍼 가져옴
                print(f"실행 중: {scraper.__class__.__name__}")
                scraped_posts = scraper.scrape()  # 스크래퍼 실행하고 반환값 받기

                # 데이터베이스에 저장
                new_posts = await handle_scraped_posts(scraped_posts)
                if new_posts:
                    print(f"새로운 post: {len(new_posts)}개")
                else:
                    print("새로운 post가 없습니다.")

                # 다시 큐 뒤로 보냄
                self.scraper_queue.append(scraper)  


