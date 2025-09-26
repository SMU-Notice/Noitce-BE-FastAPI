import re
import aiohttp
import logging
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from app.board.infra.scraper.posts.post_content_scraper import IPostContentScraper
from app.board.application.dto.summary_processed_post_dto import SummaryProcessedPostDTO
from app.board.domain.post import Post
from app.board.domain.post_picture import PostPicture

logger = logging.getLogger(__name__)


class MainBoardPostScraper(IPostContentScraper):
    """상명대 공지사항 게시판 전용 스크래퍼"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.base_url = "https://www.smu.ac.kr"
        self.content_selectors = [
            '.fr-view',           # Froala 에디터
            '.board-view-content',
            '.content',
            '.view-content',
            '#content',
            '.post-content'
        ]

    async def extract_post_content_from_url(self, post: Post) -> SummaryProcessedPostDTO:
        """
        게시물 URL에서 텍스트와 이미지를 추출하여 DTO 생성
        """
        try:
            logger.info("게시물 추출 시작 - 제목: %s, URL: %s", post.title, post.url)
            
            # HTML 가져오기 및 파싱
            soup = await self._fetch_and_parse_html(post.url)
            if not soup:
                return SummaryProcessedPostDTO.create_with_post_only(post)
            
            # 본문 영역 찾기
            post_content = self._find_post_content_area(soup)
            if not post_content:
                logger.warning("게시물 본문을 찾을 수 없음 - URL: %s", post.url)
                return SummaryProcessedPostDTO.create_with_post_only(post)
            
            # 텍스트 추출 및 정제
            text_content = self._extract_and_clean_text(post_content)
            post.original_content = text_content
            
            # 이미지 추출 및 PostPicture 생성
            post_picture = self._extract_first_image(post_content, post.original_post_id)
            
            # 결과 로깅
            text_length = len(text_content) if text_content else 0
            image_status = "이미지 있음" if post_picture else "이미지 없음"
            logger.info("추출 완료 - 텍스트: %d자, %s", text_length, image_status)
            
            return SummaryProcessedPostDTO(
                post=post,
                post_picture=post_picture
            )
            
        except Exception as e:
            logger.error("게시물 추출 중 오류 발생 - URL: %s, 오류: %s", post.url, e)
            return SummaryProcessedPostDTO.create_with_post_only(post)

    async def _fetch_and_parse_html(self, url: str):
        """HTML 가져오기 및 BeautifulSoup 파싱"""
        try:
            logger.debug("HTTP 요청 시작: %s", url)
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    response.raise_for_status()
                    html_content = await response.text(encoding='utf-8')
                    
            if not html_content:
                logger.warning("HTML 콘텐츠가 비어있음: %s", url)
                return None
                
            logger.debug("HTML 가져오기 성공 - 크기: %d bytes", len(html_content))
            return BeautifulSoup(html_content, 'html.parser')
            
        except aiohttp.ClientError as e:
            logger.error("페이지 가져오기 실패 - URL: %s, 오류: %s", url, e)
            return None

    def _find_post_content_area(self, soup):
        """게시물 본문 영역 찾기"""
        # 우선순위에 따라 셀렉터 시도
        for selector in self.content_selectors:
            content = soup.select_one(selector)
            if content:
                logger.debug("본문 영역 찾기 성공: %s", selector)
                return content
        
        # fallback: body 태그 사용
        content = soup.find('body')
        if content:
            logger.debug("본문 영역을 body 태그로 대체")
            return content
            
        return None

    def _extract_and_clean_text(self, content_element) -> str:
        """텍스트 추출 및 정제"""
        text = content_element.get_text()
        # 연속된 줄바꿈을 하나로 정리
        text = re.sub(r'\n\s*\n', '\n', text)
        # 연속된 공백을 하나로 정리
        text = re.sub(r'[ \t]+', ' ', text)
        return text.strip()

    def _extract_first_image(self, content_element, original_post_id: str):
        """첫 번째 이미지 추출하여 PostPicture 생성"""
        img_tags = content_element.find_all('img')
        
        for img in img_tags:
            src = img.get('src')
            if not src:
                continue
                
            # 절대 URL로 변환
            if src.startswith('/'):
                image_url = urljoin(self.base_url, src)
            elif src.startswith('http'):
                image_url = src
            else:
                image_url = urljoin(self.base_url, src)
            
            # 첫 번째 유효한 이미지로 PostPicture 생성
            try:
                logger.debug("PostPicture 생성 - 이미지 URL: %s", image_url)
                return PostPicture(
                    url=image_url,
                    original_post_id=original_post_id,
                )
            except Exception as e:
                logger.error("PostPicture 생성 실패 - URL: %s, 오류: %s", image_url, e)
                continue
        
        logger.debug("추출할 이미지가 없음")
        return None