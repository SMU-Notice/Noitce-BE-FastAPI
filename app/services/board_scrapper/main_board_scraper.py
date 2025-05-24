import logging
from app.services.board_scrapper.base import BoardScraper
import requests
from bs4 import BeautifulSoup
import re
from app.config.scraper_config import get_scraper_config, ScraperConfig
from typing import Dict, Any

logger = logging.getLogger(__name__)

class MainBoardScraper(BoardScraper):

    def __init__(self, config_name: str):
        """
        :param config_name: 스크래퍼 설정 이름 (예: "main_board_sangmyung", "main_board_seoul")
        """
        config = get_scraper_config(config_name)
        self.base_url = config.base_url
        self.params = config.params
        self.campus_filter = config.campus
        self.board_id = config.board_id
        self.interval = config.interval
        

    def scrape(self) -> dict:
        """게시판 데이터를 크롤링하는 메서드"""
        # 웹페이지 요청
        response = requests.get(self.base_url, params=self.params)
        response.raise_for_status()  # 요청 실패 시 예외 발생

        # HTML 파싱
        soup = BeautifulSoup(response.text, "html.parser")

        # 게시물 목록 추출
        posts = {}

        for li in soup.select(".board-thumb-wrap > li"):
            # 공지글일 경우 무시 
            if li.select_one(".noti"):
                continue

            # 캠퍼스 정보
            campus_tag = li.select_one(".cmp")
            if campus_tag:
                campus_class = campus_tag["class"]
                if self.campus_filter not in campus_class:
                    continue
                campus = "상명" if self.campus_filter == "sangmyung" else "서울"
            else:
                campus = "N/A"

            # 게시글 ID
            article_id_tag = li.select_one(".board-thumb-content-number")
            article_id = article_id_tag.get_text(strip=True) if article_id_tag else "N/A"
            article_id = re.sub(r"No\.", "", article_id).strip()  # "No." 제거

            # 게시글 URL
            article_link_tag = li.select(".board-thumb-content-title a")[1]  # 두 번째 <a> 태그를 선택
            article_url = self.base_url + article_link_tag["href"] if article_link_tag else "N/A"

            # 제목
            title_tag = li.select(".board-thumb-content-title a")[1]  # 두 번째 <a> 태그를 선택
            title = title_tag.text.strip() if title_tag else "N/A"

            # 게시 날짜
            date_tag = li.select_one(".board-thumb-content-date")
            date = date_tag.text.strip() if date_tag else "N/A"
            date = re.sub(r"작성일", "", date).strip()

            # 카테고리 (일반, 학사 등)
            category_tag = li.select_one(".cate")
            category = category_tag.text.strip("[]") if category_tag else "N/A"

            # 조회수
            views_tag = li.select_one(".board-thumb-content-views")
            views = views_tag.text.strip() if views_tag else "0"
            views = re.sub(r"조회수", "", views).strip()  # "조회수" 제거

            # 첨부파일 여부
            file_tag = li.select_one(".list-file a")
            has_attachment = True if file_tag else False  # 첨부파일이 있으면 True, 없으면 False

            # 해시 테이블에 저장
            posts[article_id] = {
                "id": article_id,
                "title": title,
                "date": date,
                "campus": campus,
                "post_type": category,
                "view_count": views,
                "url": article_url,
                "has_reference": has_attachment  
            }

        logger.info("스크랩된 post ids: %s", ', '.join(str(post_id) for post_id in posts.keys()))
        # logger.info(f"MainBoardScraper({self.campus_filter}): 완료")

        return {"board_id" : self.board_id, "count": len(posts), "data" : posts}


# 테스트 실행    
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("✅ 상명 캠퍼스 테스트:")
    sangmyung_scraper = MainBoardScraper(config_name="main_board_sangmyung")
    print(sangmyung_scraper.scrape())

    print("\n✅ 서울 캠퍼스 테스트:")
    seoul_scraper = MainBoardScraper(config_name="main_board_seoul")
    print(seoul_scraper.scrape())
