from bs4 import BeautifulSoup
import re
import aiohttp
import logging
import os
from urllib.parse import urljoin
from app.board.infra.scraper.posts.post_content_scraper import IPostContentScraper
from app.board.application.dto.summary_processed_post_dto import SummaryProcessedPostDTO
from app.board.domain.post import Post
from app.board.domain.post_picture import PostPicture
from app.board.application.summary_service import SummaryService
from app.board.application.ocr_processor import OCRProcessor
from typing import Optional, Dict

logger = logging.getLogger(__name__)

ENABLE_SUMMARY = os.getenv("ENABLE_SUMMARY", "false").lower() == "true"

class MainBoardPostScraper(IPostContentScraper):
    """상명대 공지사항 게시판 전용 스크래퍼"""
    
    def __init__(self, ocr_processor: Optional[OCRProcessor] = None):
        self.ocr_processor = ocr_processor or OCRProcessor()

    async def extract_post_from_url(self, post: Post) -> SummaryProcessedPostDTO:
        """
        공개 API - 전체 처리 플로우
        """
        try:
            logger.info("게시물 추출 시작 (게시물 이름): %s", post.title)
            logger.info("게시물 추출 시작 (게시물 url): %s", post.url)
            
            # 1단계: 콘텐츠 및 이미지 스크랩
            scrape_result = await self._scrape_content_and_images(post)
            
            # DTO 생성
            summary_processed_dto = SummaryProcessedPostDTO(
                post=post,
                post_picture=scrape_result.get('post_picture')
            )
            
            # 2단계: OCR 처리
            dto_with_ocr = await self._process_ocr_if_needed(summary_processed_dto)
            
            # 3단계: 요약 처리
            final_dto = await self._process_summary(dto_with_ocr)
            
            logger.info(f"게시물 처리 완료 - ID: {post.id}")
            return final_dto
            
        except Exception as e:
            logger.error(f"게시물 추출 중 오류 발생: {post.url} - {e}")
            return SummaryProcessedPostDTO.create_with_post_only(post)

    async def _scrape_content_and_images(self, post: Post) -> Dict:
        """
        1단계: HTML에서 본문 텍스트와 이미지를 스크랩
        """
        # 1. 웹페이지 HTML 가져오기
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        try:
            logger.debug(f"HTTP 요청 시작: {post.url}")
            async with aiohttp.ClientSession() as session:
                async with session.get(post.url, headers=headers) as response:
                    response.raise_for_status()
                    html_content = await response.text(encoding='utf-8')
                    logger.debug(f"HTTP 응답 성공 - 상태코드: {response.status}")
        except aiohttp.ClientError as e:
            logger.error(f"페이지 가져오기 실패: {post.url} - {e}")
            return {'text': '', 'post_picture': None}
        
        if not html_content:
            logger.warning(f"HTML 가져오기 실패: {post.url}")
            return {'text': '', 'post_picture': None}
        
        logger.debug(f"HTML 가져오기 성공 - 크기: {len(html_content)} bytes")
        
        # 2. BeautifulSoup으로 파싱
        soup = BeautifulSoup(html_content, 'html.parser')
        logger.debug("HTML 파싱 완료")
        
        # 3. 게시물 본문 찾기 (상명대 공지사항 구조)
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
            post_content = soup.find('body')
            if not post_content:
                logger.warning("게시물 본문을 찾을 수 없음 - body 태그도 없음")
                return {'text': '', 'post_picture': None}
            else:
                logger.debug("본문 영역을 body 태그로 대체")
        
        logger.debug("게시물 본문 영역 찾기 완료")
        
        # 4. 텍스트와 이미지 추출
        # 텍스트 추출
        text_content = post_content.get_text()
        text_content = re.sub(r'\n\s*\n', '\n', text_content)
        text_content = re.sub(r'[ \t]+', ' ', text_content)
        text_content = text_content.strip()
        
        # 이미지 URL 추출
        image_urls = []
        img_tags = post_content.find_all('img')
        
        for img in img_tags:
            src = img.get('src')
            if src:
                if src.startswith('/'):
                    full_url = urljoin("https://www.smu.ac.kr", src)
                elif src.startswith('http'):
                    full_url = src
                else:
                    full_url = urljoin("https://www.smu.ac.kr", src)
                
                image_urls.append(full_url)
                logger.debug(f"이미지 URL 추가: {full_url}")
        
        text_length = len(text_content) if text_content else 0
        image_count = len(image_urls) if image_urls else 0
        
        logger.info(f"추출 완료 - 텍스트: {text_length}자, 이미지: {image_count}개")
        
        # Post에 원본 텍스트 저장
        post.original_content = text_content

        # 5. 첫 번째 이미지 URL로 PostPicture 엔티티 생성 (있을 때만)
        post_picture = None
        if image_urls and len(image_urls) > 0:
            first_image_url = image_urls[0]
            logger.info(f"PostPicture 생성 - 이미지 URL: {first_image_url}")
            logger.info(f"전체 이미지 개수: {len(image_urls)}개 (첫 번째 이미지만 사용)")
            
            try:
                post_picture = PostPicture(
                    url=first_image_url,
                    original_post_id=post.original_post_id,
                )
                logger.debug(f"PostPicture 생성 완료 - URL: {first_image_url}")
            except Exception as e:
                logger.error(f"PostPicture 생성 중 오류 발생: {e}")
                post_picture = None
        else:
            logger.info("이미지가 없어서 PostPicture를 생성하지 않습니다")
        
        return {
            'text': text_content,
            'post_picture': post_picture
        }

    async def _process_ocr_if_needed(self, summary_processed_dto: SummaryProcessedPostDTO) -> SummaryProcessedPostDTO:
        """
        2단계: 이미지가 있으면 OCR 처리 요청
        """
        logger.info("OCR 처리 단계 시작")
        return await self.ocr_processor.process_dto(summary_processed_dto)

    async def _process_summary(self, summary_processed_dto: SummaryProcessedPostDTO) -> SummaryProcessedPostDTO:
        """
        3단계: 요약 처리 요청
        """
        summary_service = SummaryService()
        
        if ENABLE_SUMMARY:
            logger.info("ENABLE_SUMMARY=True - 요약 처리를 시작합니다")
            processed_dto = await summary_service.create_summary_processed_post(summary_processed_dto)
            logger.info("요약 처리가 완료되었습니다")
            return processed_dto
        else:
            logger.info("ENABLE_SUMMARY=False - 요약 처리를 건너뜁니다")
            return summary_processed_dto
