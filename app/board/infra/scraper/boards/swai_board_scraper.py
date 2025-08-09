import logging
import aiohttp
from bs4 import BeautifulSoup
import re
from app.board.infra.scraper.boards.board_scraper_base import BoardScraper
from app.config.scraper_config import get_scraper_config
from app.board.infra.scraper.models.scraped_post import ScrapedPost

logger = logging.getLogger(__name__)

class SwaiBoardScraper(BoardScraper):

    def __init__(self, config_name: str):
        """
        :param config_name: 스크래퍼 설정 이름 (예: "swai_notice")
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
                # 웹페이지 요청
                async with session.get(self.base_url, params=self.params) as response:
                    response.raise_for_status()
                    html_content = await response.text()

                soup = BeautifulSoup(html_content, "html.parser")
                posts = {}

                # SW중심대학사업단의 경우 tr로
                for tr in soup.select("div.tbl_head01.tbl_wrap table tbody > tr"):
                    # 공지글일 경우 무시
                    if "bo_notice" in tr.get("class", []):
                        continue

                    # 캠퍼스 정보 (없으면 N/A)
                    campus_tag = tr.select_one(".cmp")
                    if campus_tag:
                        campus_class = campus_tag.get("class", [])
                        if self.campus_filter not in campus_class:
                            continue
                        campus = "상명" if self.campus_filter == "sang" else "서울"
                    else:
                        campus = "N/A"

                    # 게시글 ID
                    article_id_tag = tr.select_one("td.td_num2")
                    original_post_id = article_id_tag.get_text(strip=True) if article_id_tag else "N/A"

                    # 게시글 URL
                    article_link_tag = tr.select_one("td.td_subject a")
                    post_url = article_link_tag["href"] if article_link_tag else "N/A"

                    # 제목
                    title_tag = tr.select_one("td.td_subject a")
                    title = title_tag.get_text(strip=True) if title_tag else "N/A"

                    # 게시 날짜
                    date_tag = tr.select_one("td.td_datetime")
                    date = date_tag.get_text(strip=True) if date_tag else "N/A"

                    # 카테고리
                    category_tag = tr.select_one(".cate")
                    post_type = category_tag.get_text(strip=True).strip("[]") if category_tag else "N/A"

                    # 조회수
                    views_tag = tr.select_one("td.td_num")
                    view_count = views_tag.get_text(strip=True) if views_tag else "0"

                    # 첨부파일 여부
                    file_tag = tr.select_one(".list-file a")
                    has_reference = True if file_tag else False #SW중심대학사업단은 첨부파일 유무 표시 안됨

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

if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)

    async def test():
        print("✅ SW중심대학사업단 공지사항 테스트:")
        swai_scraper = SwaiBoardScraper(config_name="swai_notice")
        result = await swai_scraper.scrape()
        print(result)

    asyncio.run(test())
