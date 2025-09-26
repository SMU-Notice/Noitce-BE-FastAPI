import logging
import aiohttp
from bs4 import BeautifulSoup
import re

from app.board.infra.scraper.boards.board_scraper_base import BoardScraper
from app.config.scraper_config import get_scraper_config
from app.board.infra.scraper.models.scraped_post import ScrapedPost

logger = logging.getLogger(__name__)


class MajorBoardScraper(BoardScraper):
    def __init__(self, config_name: str):
        config = get_scraper_config(config_name)
        self.base_url = config.base_url
        self.params = config.params or {}
        self.campus_filter = config.campus     # "seoul" 또는 "sangmyung"
        self.board_id = config.board_id
        self.interval = config.interval

    async def scrape(self) -> dict:
        """학부·학과 게시판을 비동기로 크롤링합니다."""
        campus = "서울" if self.campus_filter == "seoul" else "상명"    #학과게시판은 모두 seoul로 설정

        async with aiohttp.ClientSession() as session:
            try:
                # 웹페이지 요청
                async with session.get(self.base_url, params=self.params) as response:
                    response.raise_for_status()
                    html_content = await response.text()

                # HTML 파싱
                soup = BeautifulSoup(html_content, "html.parser")
                posts = {}

                for li in soup.select(".board-thumb-wrap > li"):
                    link_tag = li.select_one(".board-thumb-content-title a")    #제목 a태그로 필터링
                    if not link_tag:
                        continue  

                    href = link_tag["href"]
                    # articleNo로 게시물 번호 추출
                    m = re.search(r"articleNo=(\d+)", href)
                    if not m:
                        continue  # 없으면 건너뛰기
                    original_post_id = m.group(1) # 매칭된 숫자 지정

                    # 링크
                    post_url = href if href.startswith("http") else self.base_url + href    #http있으면 그대로 이용, 없으면 기존 링크에 붙임

                    #제목
                    title = link_tag.get_text(strip=True)

                    # 게시 날짜
                    date_tag = li.select_one(".board-thumb-content-date")
                    date = (
                        date_tag.get_text(strip=True)
                        .replace("작성일", "")
                        .strip()
                        .replace(".", "-")
                        if date_tag else "N/A"
                    )
                    # 조회수
                    views_tag = li.select_one(".board-thumb-content-views")
                    view_count = (
                        re.sub(r"조회수", "", views_tag.get_text(strip=True)).strip()
                        if views_tag else "0"
                    )

                    # 카테고리
                    post_type = "기본"

                    # 첨부파일 여부
                    file_tag = li.select_one("div.file_downWrap ul.filedown_list li")
                    has_reference = bool(file_tag)
                    
                    # — (7) Pydantic 모델에 저장
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

                logger.info("스크랩된 post ids: %s", ", ".join(posts.keys()))
                return {"board_id": self.board_id, "scraped_count": len(posts), "data": posts}

            except aiohttp.ClientError as e:
                logger.error(f"HTTP 클라이언트 오류: {e}")
                raise
            except Exception as e:
                logger.error(f"스크래핑 중 예상치 못한 오류: {e}")
                raise

