from services.board_scrapper.base import BoardScraper

class ExampleScraper1(BoardScraper):
    def scrape(self) -> dict:
        # 예시: 데이터를 딕셔너리 형태로 반환
        print("ExampleScraper1: 데이터를 긁어옴")
        return {"title": "Example1", "content": "Scraped content 1"}

class ExampleScraper2(BoardScraper):
    def scrape(self) -> dict:
        print("ExampleScraper2: 데이터를 긁어옴")
        return {"title": "Example2", "content": "Scraped content 2"}
