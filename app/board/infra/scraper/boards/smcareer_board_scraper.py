import logging
import aiohttp
from bs4 import BeautifulSoup
import re
import asyncio
from app.board.infra.scraper.boards.board_scraper_base import BoardScraper
from app.config.scraper_config import get_scraper_config
from app.board.infra.scraper.models.scraped_post import ScrapedPost

logger = logging.getLogger(__name__)

class SmCareerBoardScraper(BoardScraper):

    def __init__(self, config_name: str):
        config = get_scraper_config(config_name)
        self.base_url      = config.base_url
        self.params        = config.params
        self.campus_filter = config.campus
        self.board_id      = config.board_id
        self.interval      = config.interval


    # 비동기로 상세 페이지에서 첨부파일 유무만 확인
    async def _detail_has_attachment(self, session: aiohttp.ClientSession, url: str, sem: asyncio.Semaphore) -> bool:
        
        if not url:
            return False
        async with sem:
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    resp.raise_for_status()
                    html = await resp.text()

            except Exception as e:
                logger.debug(f"첨부 확인 실패({url}): {e}")
                return False
            
        soup = BeautifulSoup(html, "html.parser")

        # "파일첨부" 행 탐색
        attach_td = None
        for tr in soup.select("table.table_view tr"):
            th = tr.find("th")
            if th and th.get_text(strip=True) == "파일첨부":
                attach_td = tr.find("td")
                break

        if not attach_td:
            return False

        # 해당 td 내부의 실제 파일 링크 존재 여부 확인
        for a in attach_td.select("a[href]"):
            href = a.get("href", "")
            text = a.get_text(" ", strip=True)
            if (
                "_app/file/file_read.asp" in href
                or any(href.lower().endswith(ext) for ext in (".pdf", ".hwp", ".hwpx", ".doc", ".docx", ".xls", ".xlsx", ".zip"))
                or any(k in text for k in ("다운로드", "Download"))
            ):
                return True

        return False


    async def scrape(self) -> dict:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.base_url, params=self.params) as response:
                    response.raise_for_status()
                    html_content = await response.text()

                soup = BeautifulSoup(html_content, "html.parser")
                posts = {}

                #  tr 기준으로 작업
                for tr in soup.select("table.table_list tbody > tr"):

                    # 캠퍼스 정보 두 번째 center td 사용 - 공통 서울 천안 구분 필요
                    campus_td = tr.select("td.center")[1]
                    campus = campus_td.get_text(strip=True)

                    # 게시글 ID 첫 번째 center td 사용
                    id_td = tr.select("td.center")[0]
                    original_post_id = id_td.get_text(strip=True)

                    # 게시글 URL: button.onclick 에서 꺼내기
                    btn = tr.select_one("button.button_view")
                    onclick = btn.get("onclick", "")
                    m = re.search(r"location\.href='([^']+)'", onclick)
                    href = m.group(1) if m else ""
                    post_url = href if href.startswith("http") else self.base_url.rsplit('/', 1)[0] + '/' + href

                    # 제목 세 번째 td 안의 <p>
                    title_p = tr.select("td")[2].select_one("p")
                    title   = title_p.get_text(strip=True) if title_p else "N/A"

                    # 게시 날짜 (등록일): 여섯 번째 td 안의 <p>
                    date_p  = tr.select("td")[5].select_one("p")
                    raw_date = date_p.get_text(strip=True) if date_p else ""
                    # 날짜 형식 변경 YYYY-MM-DD로 맞춰주기 위해 파싱
                    parts = raw_date.split(".")
                    if len(parts) == 3:
                        yy, mm, dd = parts
                        date = f"20{yy}-{mm.zfill(2)}-{dd.zfill(2)}"
                    else:
                        date = raw_date

                    # 카테고리: 기본값으로
                    post_type = "N/A"

                    # 조회수: 다섯 번째 td 안의 <p>
                    view_p     = tr.select("td")[4].select_one("p")
                    view_count = view_p.get_text(strip=True) if view_p else "0"

                    # 첨부파일 여부의 경우 우선적으로 None으로 설정 후 덮어 씌우기
                    has_reference = False

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

                # ✅ 상세 페이지에서 첨부 여부 비동기 확인 (동시성 제한)
                sem = asyncio.Semaphore(5)
                tasks = [self._detail_has_attachment(session, p.url, sem) for p in posts.values()]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for post, has_att in zip(posts.values(), results):
                    post.has_reference = (has_att is True)
                                          
                logger.info("스크랩된 post ids: %s", ", ".join(posts.keys()))
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
        print("✅ 대학일자리플러스센터 테스트:")
        scraper = SmCareerBoardScraper(config_name="sm_career")
        result = await scraper.scrape()
        print(result)

    asyncio.run(test())
