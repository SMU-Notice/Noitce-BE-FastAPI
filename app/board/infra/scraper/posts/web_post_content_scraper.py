from bs4 import BeautifulSoup
import re
import aiohttp
import logging
from urllib.parse import urljoin
from app.board.application.ports.post_content_scraping_port import PostContentScraperPort
from app.board.application.dto.scraped_content import ScrapedContent
from app.board.application.dto.processed_post_dto import ProcessedPostDTO
import app.board.domain.post as Post
from app.board.application.summary_service import SummaryService


# 로거 설정
logger = logging.getLogger(__name__)


class WebPostContentScraper(PostContentScraperPort):
    async def extract_post_from_url(self, post: Post) -> ProcessedPostDTO:
        """
        URL에서 게시물 내용을 추출하는 메서드
        
        Args:
            post: 추출할 게시물 Post 객체
            
        Returns:
            ProcessedPostDTO: Post, Location, OCR 엔티티를 포함한 처리 결과
        """
        summary_service = SummaryService()

        try:
            logger.info("게시물 추출 시작 (게시물 이름): %s", post.title)
            logger.info("게시물 추출 시작 (게시물 url): %s", post.url)
            
            # 1. 웹페이지 HTML 가져오기
            html_content = await self._fetch_page_content(post.url)
            if not html_content:
                logger.warning(f"HTML 가져오기 실패: {post.url}")
                return ProcessedPostDTO.create_with_post_only(post)
            
            logger.debug(f"HTML 가져오기 성공 - 크기: {len(html_content)} bytes")
            
            # 2. BeautifulSoup으로 파싱
            soup = BeautifulSoup(html_content, 'html.parser')
            logger.debug("HTML 파싱 완료")
            
            # 3. 게시물 본문 찾기
            post_content = self._find_post_content(soup)
            if not post_content:
                logger.warning(f"게시물 본문을 찾을 수 없음: {post.url}")
                return ProcessedPostDTO.create_with_post_only(post)
            
            logger.debug("게시물 본문 영역 찾기 완료")
            
            # 4. 텍스트와 이미지 추출
            result = self._extract_content(str(post_content), post.url)
            
            text_length = len(result['text']) if result['text'] else 0
            image_count = len(result['image_urls']) if result['image_urls'] else 0
            
            logger.info(f"추출 완료 - 텍스트: {text_length}자, 이미지: {image_count}개")
            
            # 5. ScrapedContent 생성
            scraped_content = ScrapedContent(
                text=result['text'],
                image_urls=result['image_urls']
            )

            # 6. SummaryService를 사용하여 요약과 Location 정보 추출
            processed_dto = await summary_service.create_summary_and_location(post, scraped_content)
            
            return processed_dto
            
        except Exception as e:
            logger.error(f"게시물 추출 중 오류 발생: {post.url} - {e}")
            return ProcessedPostDTO.create_with_post_only(post)

    async def _fetch_page_content(self, url: str) -> str:
        """
        웹페이지에서 HTML 내용을 가져오는 내부 함수
        
        Args:
            url: 가져올 웹페이지 URL
        
        Returns:
            HTML 내용 또는 None (실패 시)
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        try:
            logger.debug(f"HTTP 요청 시작: {url}")
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    response.raise_for_status()  # HTTP 에러 체크
                    text = await response.text(encoding='utf-8')  # 한글 깨짐 방지
                    logger.debug(f"HTTP 응답 성공 - 상태코드: {response.status}")
                    return text
        except aiohttp.ClientError as e:
            logger.error(f"페이지 가져오기 실패: {url} - {e}")
            return None

    def _find_post_content(self, soup: BeautifulSoup):
        """
        게시물 본문 영역을 찾는 내부 함수
        
        Args:
            soup: BeautifulSoup 객체
            
        Returns:
            본문 영역 element 또는 None
        """
        # 게시물 본문 찾기 (상명대 공지사항 페이지 구조에 맞춰)
        content_selectors = [
            '.fr-view',           # Froala 에디터
            '.board-view-content',
            '.content',
            '.view-content',
            '#content',
            '.post-content'
        ]
        
        post_content = None
        for selector in content_selectors:
            post_content = soup.select_one(selector)
            if post_content:
                logger.debug(f"본문 영역 찾기 성공: {selector}")
                break
        
        if not post_content:
            # 선택자로 찾지 못했을 때 전체 body에서 추출
            post_content = soup.find('body')
            if not post_content:
                logger.warning("게시물 본문을 찾을 수 없음 - body 태그도 없음")
                return None
            else:
                logger.debug("본문 영역을 body 태그로 대체")
        
        return post_content

    def _extract_content(self, html_content: str, base_url: str = "https://www.smu.ac.kr") -> dict:
        """
        HTML에서 텍스트와 이미지 URL을 추출하는 내부 함수
        
        Args:
            html_content: 게시물 HTML 내용
            base_url: 상대 URL을 절대 URL로 변환할 베이스 URL
        
        Returns:
            {'text': str, 'image_urls': list}
        """
        # BeautifulSoup으로 HTML 파싱
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 텍스트 추출
        text_content = soup.get_text()
        
        # 불필요한 공백 제거 및 정리
        text_content = re.sub(r'\n\s*\n', '\n', text_content)  # 연속된 빈 줄 제거
        text_content = re.sub(r'[ \t]+', ' ', text_content)     # 연속된 공백 제거
        text_content = text_content.strip()                      # 앞뒤 공백 제거
        
        logger.debug(f"텍스트 추출 완료 - 길이: {len(text_content)}자")
        
        # 이미지 URL 추출
        image_urls = []
        img_tags = soup.find_all('img')
        
        logger.debug(f"이미지 태그 발견: {len(img_tags)}개")
        
        for img in img_tags:
            src = img.get('src')
            if src:
                # 상대 URL을 절대 URL로 변환
                if src.startswith('/'):
                    full_url = urljoin(base_url, src)
                elif src.startswith('http'):
                    full_url = src
                else:
                    full_url = urljoin(base_url, src)
                
                image_urls.append(full_url)
                logger.debug(f"이미지 URL 추가: {full_url}")
        
        logger.debug(f"최종 이미지 URL 개수: {len(image_urls)}개")
        
        return {
            'text': text_content,
            'image_urls': image_urls
        }


# 사용 예시
if __name__ == "__main__":
    import asyncio
    
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('scraper.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    async def test_scraper():
        # URL에서 직접 추출
        url = "https://www.smu.ac.kr/kor/life/notice.do?mode=view&articleNo=757659"
        
        print("웹페이지에서 내용을 가져오는 중...")
        logger.info("=== 스크래핑 테스트 시작 ===")
        
        scraper = WebPostContentScraper()
        result = await scraper.extract_post_from_url(url)
        
        if result.text or result.image_urls:
            print("=== 추출된 텍스트 ===")
            print(result.text)
            
            print("\n=== 추출된 이미지 URLs ===")
            if result.image_urls:
                for i, img_url in enumerate(result.image_urls, 1):
                    print(f"{i}. {img_url}")
                print(f"\n총 {len(result.image_urls)}개의 이미지가 발견되었습니다.")
                logger.info(f"테스트 완료 - 이미지 {len(result.image_urls)}개 발견")
            else:
                print("이미지가 없습니다.")
                logger.info("테스트 완료 - 이미지 없음")
        else:
            print("내용 추출에 실패했습니다.")
            logger.error("테스트 실패 - 내용 추출 불가")
        
        logger.info("=== 스크래핑 테스트 완료 ===")
    
    # 비동기 함수 실행
    asyncio.run(test_scraper())