import logging
import aiohttp
from bs4 import BeautifulSoup
import re
from app.board.infra.scraper.boards.board_scraper_base import BoardScraper
from app.config.scraper_config import get_scraper_config
from app.board.infra.scraper.models.scraped_post import ScrapedPost

logger = logging.getLogger(__name__)

class AdditionalBoardScraper(BoardScraper):

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
                    response.raise_for_status()
                    html_content = await response.text()

                # HTML 파싱
                soup = BeautifulSoup(html_content, "html.parser")
                posts = {}

                for li in soup.select(".board-thumb-wrap > li"):
                    # 공지글일 경우 무시
                    if li.select_one(".noti"):
                        continue

                    # 캠퍼스 정보
                    campus_tag = li.select_one(".cmp")
                    if campus_tag:
                        campus_class = campus_tag.get("class", [])
                        if self.campus_filter not in campus_class:
                            continue
                        campus = "상명" if self.campus_filter == "sang" else "서울"
                    else:
                        campus = "N/A"

                    # 게시글 ID
                    link_for_id = li.select(".board-thumb-content-title a")[0]  # 상명대 통합공지와 다르게 첫번째 태그 이용
                    match = re.search(r"articleNo=(\d+)", link_for_id["href"])
                    original_post_id = match.group(1) if match else "N/A"

                    # 게시글 URL
                    article_link_tag = li.select(".board-thumb-content-title a")[0]
                    post_url = self.base_url + article_link_tag["href"] if article_link_tag else "N/A"

                    # 제목
                    title_tag = li.select(".board-thumb-content-title a")[0]
                    title = title_tag.get_text(separator=" ", strip=True) if title_tag else "N/A"

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
                    view_count = re.sub(r"조회수", "", view_count).strip()

                    # 첨부파일 여부
                    file_tag = li.select_one(".list-file a")
                    has_reference = True if file_tag else False

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
        print("✅ 상명행복 기숙사 테스트:")
        happydorm_scraper = AdditionalBoardScraper(config_name="happydorm_notice")
        result1 = await happydorm_scraper.scrape()
        print(result1)

        print("\n✅ 스뮤하우스 테스트:")
        smudorm_scraper = AdditionalBoardScraper(config_name="smudorm_notice")
        result2 = await smudorm_scraper.scrape()
        print(result2)

        print("\n✅ 대외협력처 테스트:")
        foreign_scraper = AdditionalBoardScraper(config_name="foreign_notice")
        result3 = await foreign_scraper.scrape()
        print(result3)

        print("\n✅ 일반대학원 테스트:")
        grad_scraper = AdditionalBoardScraper(config_name="grad_notice")
        result4 = await grad_scraper.scrape()
        print(result4)

        print("\n✅ 공학교육혁신센터 테스트:")
        icee_scraper = AdditionalBoardScraper(config_name="grad_notice")
        result5 = await icee_scraper.scrape()
        print(result5)

    # 비동기 실행
    asyncio.run(test_scrapers())
