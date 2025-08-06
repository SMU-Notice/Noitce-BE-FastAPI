import logging
import aiohttp
from bs4 import BeautifulSoup
import re
from app.board.infra.scraper.boards.board_scraper_base import BoardScraper
from app.config.scraper_config import get_scraper_config
from app.board.infra.scraper.models.scraped_post import ScrapedPost

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

    async def scrape(self) -> dict:
        """게시판 데이터를 크롤링하는 메서드 (비동기)"""
        async with aiohttp.ClientSession() as session:
            try:
                # 웹페이지 요청 (비동기)
                async with session.get(self.base_url, params=self.params) as response:
                    response.raise_for_status()  # 요청 실패 시 예외 발생
                    html_content = await response.text()

                # HTML 파싱
                soup = BeautifulSoup(html_content, "html.parser")

                # 게시물 목록 추출
                posts = {}

                for li in soup.select(".board-thumb-wrap > li"):
                    # # 공지글일 경우 무시 -> 학교 홈페이지에서 공지 사항일 경우 일반글에 나오지 않게 바꿈
                    # if li.select_one(".noti"):
                    #     continue

                    # 캠퍼스 정보
                    campus_tag = li.select_one(".cmp")
                    if campus_tag:
                        campus_class = campus_tag["class"]
                        if self.campus_filter not in campus_class:
                            continue
                        campus = "상명" if self.campus_filter == "sang" else "서울"
                    else:
                        campus = "N/A"

                    # 게시글 ID
                    article_id_tag = li.select_one(".board-thumb-content-number")
                    original_post_id = article_id_tag.get_text(strip=True) if article_id_tag else "N/A"
                    original_post_id = re.sub(r"No\.", "", original_post_id).strip()  # "No." 제거

                    # 게시글 URL
                    article_link_tag = li.select(".board-thumb-content-title a")[1]  # 두 번째 <a> 태그를 선택
                    post_url = self.base_url + article_link_tag["href"] if article_link_tag else "N/A"

                    # 제목
                    title_tag = li.select(".board-thumb-content-title a")[1]  # 두 번째 <a> 태그를 선택
                    title = title_tag.text.strip() if title_tag else "N/A"

                    # 게시 날짜
                    date_tag = li.select_one(".board-thumb-content-date")
                    date = date_tag.text.strip() if date_tag else "N/A"
                    date = re.sub(r"작성일", "", date).strip()

                    # 카테고리 (일반, 학사 등)
                    category_tag = li.select_one(".cate")
                    post_type = category_tag.text.strip("[]") if category_tag else "N/A"

                    # 조회수
                    views_tag = li.select_one(".board-thumb-content-views")
                    view_count = views_tag.text.strip() if views_tag else "0"
                    view_count = re.sub(r"조회수", "", view_count).strip()  # "조회수" 제거

                    # 첨부파일 여부
                    file_tag = li.select_one(".list-file a")
                    has_reference = True if file_tag else False  # 첨부파일이 있으면 True, 없으면 False

                    # Pydantic 모델을 사용하여 데이터 저장
                    post_data = ScrapedPost(
                        original_post_id=original_post_id,
                        title=title,
                        date=date,
                        campus=campus,
                        post_type=post_type,
                        view_count=view_count,
                        url=post_url,
                        has_reference=has_reference
                    )
                    posts[original_post_id] = post_data

                logger.info("스크랩된 post ids: %s", ', '.join(str(original_post_id) for original_post_id in posts.keys()))

                return {"board_id": self.board_id, "scraped_count": len(posts), "data": posts}

            except aiohttp.ClientError as e:
                logger.error(f"HTTP 클라이언트 오류: {e}")
                raise
            except Exception as e:
                logger.error(f"스크래핑 중 예상치 못한 오류: {e}")
                raise


# 테스트 실행    
if __name__ == "__main__":
    import asyncio
    
    logging.basicConfig(level=logging.INFO)

    async def test_scrapers():
        print("✅ 상명 캠퍼스 테스트:")
        sangmyung_scraper = MainBoardScraper(config_name="main_board_sangmyung")
        result1 = await sangmyung_scraper.scrape()
        print(result1)

        print("\n✅ 서울 캠퍼스 테스트:")
        seoul_scraper = MainBoardScraper(config_name="main_board_seoul")
        result2 = await seoul_scraper.scrape()
        print(result2)

    # 비동기 실행
    asyncio.run(test_scrapers())