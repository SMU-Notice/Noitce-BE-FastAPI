import logging
from typing import List
from sqlalchemy.exc import SQLAlchemyError
from app.board.infra.repository.post_repo import PostRepository
from app.board.domain.post import Post as PostVO
from app.board.application.ports.post_content_scraping_port import PostContentScraperPort
from app.board.infra.scraper.posts.web_post_content_scraper import WebPostContentScraper
from app.board.application.dto.processed_post_dto import ProcessedPostDTO
from app.board.infra.repository.event_location_time_repo import EventLocationTimeRepository
import os


logger = logging.getLogger(__name__)


class NewPostHandler:
    """새로운 게시물 처리 전용 클래스"""
    
    def __init__(self, post_repo: PostRepository = None, content_scraper: PostContentScraperPort = None, location_repo: EventLocationTimeRepository = None):
        self.post_repo = post_repo or PostRepository()
        # 환경변수로 상세 스크랩 여부 결정
        self.enable_scraping = os.environ.get("ENABLE_DETAIL_SCRAPING", "false").lower() == "true"
        self.content_scraper = content_scraper or (WebPostContentScraper() if self.enable_scraping else None)
        self.location_repo = location_repo or EventLocationTimeRepository()
    
    async def handle_new_posts(self, new_posts: List[PostVO]) -> List[PostVO]:
        """
        새로운 게시물들을 처리 (저장) 후 저장된 데이터 반환
        
        Parameters:
        - new_posts: 저장할 신규 PostVO 객체 목록
        
        Returns:
        - List[PostVO]: 저장된 게시물 객체 목록 (ID 등 DB에서 생성된 값 포함)
        """
        processed_posts = []
        location_entities = []
        ocr_entities = []

        
        for post in new_posts:
            logger.info("NewPostHandler: 신규 게시물 처리 시작 (게시물 이름): %s", post.title)

            # 필요시 게시물 전처리 작업 수행
            # 예: 데이터 검증, 변환 등
            if not post.title or not post.url:
                logger.warning("필수 필드 누락된 게시물 스킵: %s", post)
                continue

            try:
                if self.enable_scraping and self.content_scraper:
                    processed_dto: ProcessedPostDTO = await self.content_scraper.extract_post_from_url(post)
                    logger.info("게시물 내용 추출 완료: %s", processed_dto.post.title)
                    
                    # Post 객체 추가
                    processed_posts.append(processed_dto.post)
                    
                    # Location 엔티티가 있으면 추가
                    if processed_dto.has_location():
                        location_entities.append(processed_dto.location)
                        logger.info("위치 정보 추가: %s", processed_dto.location.location)
                    
                    # OCR 엔티티가 있으면 추가 (현재는 구현되지 않음)
                    if processed_dto.has_ocr():
                        ocr_entities.append(processed_dto.ocr_entity)
                        logger.info("OCR 정보 추가")
                else:
                    # 그냥 받은 post 그대로 저장
                    processed_posts.append(post)
                    logger.info("게시물 내용 추출 완료 (스크래핑 비활성화): %s", post.title)
            
            except Exception as e:
                logger.error("게시물 내용 추출 중 오류 발생: %s - %s", post.title, e)
                continue

        try:
            # 1. Post 엔티티 저장
            saved_posts = await self.post_repo.create_posts(processed_posts)
            logger.info("NewPostHandler: %d개 신규 게시물 저장 완료", len(saved_posts))

            # 2. Location 엔티티 저장 (있는 경우에만)
            if location_entities:
                try:
                    # saved_posts에서 post_id 매핑 생성
                    post_id_mapping = {post.original_post_id: post.id for post in saved_posts}
                    
                    # Location 엔티티에 post_id 설정
                    for location_entity in location_entities:
                        if location_entity.original_post_id:
                            post_id = post_id_mapping.get(int(location_entity.original_post_id))
                            if post_id:
                                location_entity.post_id = post_id
                            else:
                                logger.warning(f"original_post_id {location_entity.original_post_id}에 해당하는 post_id를 찾을 수 없음")
                        else:
                            logger.warning("Location 엔티티에 original_post_id가 설정되지 않음")
                    
                    # Location 엔티티 저장
                    saved_locations = await self.location_repo.create_event_location_times(location_entities)
                    logger.info("NewPostHandler: %d개 위치 정보 저장 완료", len(saved_locations))
                except Exception as e:
                    logger.error("위치 정보 저장 중 오류 발생: %s", e)

            # 3. OCR 엔티티 저장 (현재는 구현되지 않음)
            if ocr_entities:
                logger.info("OCR 엔티티 저장 로직은 아직 구현되지 않음")

            return saved_posts
        except SQLAlchemyError as e:
            logger.error("NewPostHandler: 저장 실패: %s", e)
            raise