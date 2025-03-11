from abc import ABC, abstractmethod

class BoardScraper(ABC):
    @abstractmethod
    def scrape(self) -> any:
        """게시판 데이터를 긁어오는 메서드 (각 스크래퍼에서 구현 필요)"""
        pass
