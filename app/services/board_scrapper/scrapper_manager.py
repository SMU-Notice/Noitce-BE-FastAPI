import logging
from collections import deque  # 단일 스레드에서 사용 예정
from app.services.board_scrapper.base import BoardScraper
from app.services.board_scrapper.scrapper_handler import handle_scraped_posts

logger = logging.getLogger(__name__)

## 전략 패턴 

class BoardScraperManager:
    def __init__(self):
        self.scraper_queue = deque()  

    def add_scraper(self, scraper: BoardScraper):
        """
        새로운 스크래퍼를 큐에 추가
        """
        self.scraper_queue.append(scraper)
        logger.info("스크래퍼 추가됨: %s", scraper.__class__.__name__)

    async def execute_next_scraper(self):
        """
        큐에서 제일 앞에 있는 스크래퍼 실행 후 다시 큐 뒤로 보냄
        """
        if self.scraper_queue:
            scraper = self.scraper_queue.popleft()  # deque에서 맨 앞의 스크래퍼 가져옴
            logger.info("스크래퍼 실행 시작: %s", scraper.__class__.__name__)
            scraped_posts = scraper.scrape()  # 스크래퍼 실행하고 반환값 받기
            logger.info("%s 스크래핑 완료, 게시글 수: %d", scraper.__class__.__name__, scraped_posts.get("count", 0))

            # 데이터베이스에 저장
            new_posts = await handle_scraped_posts(scraped_posts)
            
            if new_posts:
                ids = [str(post.original_post_id) for post in new_posts]
                logger.info("새로운 게시물 저장 완료: original_post_ids=%s", ', '.join(ids))
            else:
                logger.info("새로운 게시물이 없습니다.")

            logger.info("스크래퍼 실행 완료: %s", scraper.__class__.__name__)
            logger.info("-------------------------")    

            # 다시 큐 뒤로 보냄
            self.scraper_queue.append(scraper)
            logger.info("스크래퍼 큐 뒤로 이동: %s", scraper.__class__.__name__)
