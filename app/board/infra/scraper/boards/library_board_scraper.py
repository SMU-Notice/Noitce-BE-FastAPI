import logging
import aiohttp
import re
from bs4 import BeautifulSoup

from app.board.infra.scraper.boards.board_scraper_base import BoardScraper
from app.config.scraper_config import get_scraper_config
from app.board.infra.scraper.models.scraped_post import ScrapedPost

logger = logging.getLogger(__name__)

class LibraryBoardScraper(BoardScraper):

    def __init__(self, config_name: str):
        """
        :param config_name: "lib_notice" 또는 "lib_eduboard"
        """
        config = get_scraper_config(config_name)
        self.base_url      = config.base_url     
        self.params        = config.params.copy() 
        self.campus_filter = config.campus       
        self.board_id      = config.board_id
        self.interval      = config.interval

    async def scrape(self) -> dict:
        """학술정보관 공지사항 / 교육공지 크롤링"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.base_url, params=self.params) as response:
                    response.raise_for_status()
                    html = await response.text()

                soup = BeautifulSoup(html, "html.parser")
                posts = {}

                # CSS 선택자로 설정 반복
                for dl in soup.select("dl.onroad-board"):
                    # 고정 공지 스킵
                    if dl.select_one("i.fa-thumbtack"):
                        continue

                    # 게시글 ID 선택
                    num_tag = dl.select_one("dt.onroad-board-number")
                    original_post_id = num_tag.get_text(strip=True) if num_tag else "N/A"

                    #링크
                    a = dl.select_one("dd > a") #<a> 태그 선별  
                    href = a["href"] if a and a.has_attr("href") else "" #href 가진 a만 읽어들이고 아니면 빈 문자열 넘김
                    # http가 붙어있는 링크면 그대로, 아니면 self.base_url에 붙여서 완성시킴
                    if href.startswith("http"):
                        post_url = href
                    else:
                        post_url = self.base_url + href

                    # 제목
                    title = a.get_text(strip=True) if a else "N/A"

                    # 게시 날짜 (dd 텍스트에서 '게시일' 뒤의 yyyy.mm.dd)
                    dd_text = dl.get_text(" ", strip=True)
                    date_match = re.search(r"게시일\s*([\d\.]+)", dd_text) #게시일 단어 뒤에 오는 날짜(숫자나 온점)를 캡처 
                    date = date_match.group(1) if date_match else "N/A"

                    date = date.replace(".", "-") #yyyy.mm.dd 를 yyyy-mm-dd로 변경 

                    # 카테고리 버튼 (일반, 학사 등)
                    post_type = "기본"

                    if post_type and title.startswith(post_type):
                        title = title[len(post_type):].strip()  #카테고리식으로 들어간 앞 단어(ex. [학술]) 제거

                    # 조회수 
                    views_match = re.search(r"조회수\s*?(\d+)", dd_text)    #조회수 뒤에 오는 숫자만 인식
                    view_count = views_match.group(1) if views_match else "0"

                    # 첨부파일 여부
                    has_reference = bool(dl.select_one("dd img.sponge-file-type-icon"))

                    # 학술정보관의 경우 캠퍼스는 서울로 고정
                    campus = "서울" if self.campus_filter == "seoul" else "N/A"

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
                logger.error("HTTP 클라이언트 오류: %s", e)
                raise
            except Exception as e:
                logger.error("스크래핑 중 예상치 못한 오류: %s", e)
                raise


# 테스트 실행
if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)

    async def test():
        print("✅ 학술정보관 공지사항 테스트:")
        notice = LibraryBoardScraper("lib_notice")
        res1 = await notice.scrape()
        print(res1)

        print("\n✅ 학술정보관 교육공지 테스트:")
        edu = LibraryBoardScraper("lib_eduboard")
        res2 = await edu.scrape()
        print(res2)

    asyncio.run(test())
