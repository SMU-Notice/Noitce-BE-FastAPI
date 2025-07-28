import logging
from typing import List
from sqlalchemy.exc import SQLAlchemyError
from app.board.infra.repository.post_repo import PostRepository
from app.board.domain.post import Post
from app.board.application.ports.post_content_scraping_port import PostContentScraperPort
from app.board.infra.scraper.posts.web_post_content_scraper import WebPostContentScraper
from app.board.application.dto.summary_processed_post_dto import SummaryProcessedPostDTO
from app.board.infra.repository.post_picture_repo import PostPictureRepository
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
        self.post_picture_repo = PostPictureRepository()
    
    async def handle_new_posts(self, new_posts: List[Post]) -> List[Post]:
        """
        새로운 게시물들을 처리 (저장) 후 저장된 데이터 반환
        
        Parameters:
        - new_posts: 저장할 신규 PostVO 객체 목록
        
        Returns:
        - List[PostVO]: 저장된 게시물 객체 목록 (ID 등 DB에서 생성된 값 포함)
        """
        processed_new_posts = []
        location_entities = []
        post_picture_entites = []

        
        for post in new_posts:
            logger.info("NewPostHandler: 신규 게시물 처리 시작 (게시물 이름): %s", post.title)

            # 필요시 게시물 전처리 작업 수행
            # 예: 데이터 검증, 변환 등
            if not post.title or not post.url:
                logger.warning("필수 필드 누락된 게시물 스킵: %s", post)
                continue

            try:
                if self.enable_scraping and self.content_scraper:
                    summary_processed_dto: SummaryProcessedPostDTO = await self.content_scraper.extract_post_from_url(post)
                    logger.info("게시물 내용 추출 완료: %s", summary_processed_dto.post.title)
                    logger.info("게시물 내용 추출 디버그 정보: %s", summary_processed_dto.post.content_summary[:10] + "...")  # 요약의 일부만 로그에 남김
                    logger.debug("게시물 내용 추출 세부 정보: %s", summary_processed_dto.post.content_summary[:100] + "...")  # 요약의 일부만 로그에 남김
                    
                    # Post 객체 추가
                    processed_new_posts.append(summary_processed_dto.post)


                    # OCR 엔티티가 있으면 추가 (현재는 구현되지 않음)
                    if (summary_processed_dto.has_post_picture() and summary_processed_dto.post_picture.picture_summary not in [None, "실패"]):
                        post_picture_entites.append(summary_processed_dto.post_picture)
                        logger.info("OCR 정보 추가")
                    else:
                        logger.info("OCR 정보가 없거나 요약 실패: %s", summary_processed_dto.post.title)
                    
                    # Location 엔티티가 있으면 추가
                    if summary_processed_dto.has_location():
                        location_entities.append(summary_processed_dto.location)
                        logger.info("위치 정보 추가: %s", summary_processed_dto.location.location)
                    else:
                        logger.info("위치 정보가 없거나 추출 실패: %s", summary_processed_dto.post.title)

                else:
                    # 그냥 받은 post 그대로 저장
                    processed_new_posts.append(post)
                    logger.info("게시물 내용 추출 완료 (스크래핑 비활성화): %s", post.title)
            
            except Exception as e:
                logger.error("게시물 내용 추출 중 오류 발생: %s - %s", post.title, e)
                continue

        try:
            # 1. 신규 게시물 저장
            try:
                saved_posts = await self._save_new_posts(processed_new_posts)
            except Exception as e:
                logger.error("NewPostHandler: 게시물 저장 실패: %s", e)
                raise

            # 2. 사진 있으면 저장
            if post_picture_entites:
                try:
                    await self._process_ocr_entities(post_picture_entites, saved_posts)
                except Exception as e:
                    logger.error("NewPostHandler: OCR 엔티티 처리 실패: %s", e)
                    raise

            # # 3. Location 엔티티 처리
            # if location_entities:
            #     try:
            #         await self._process_location_entities(location_entities, saved_posts)
            #     except Exception as e:
            #         logger.error("NewPostHandler: Location 엔티티 처리 실패: %s", e)
            #         raise

            return saved_posts

        except Exception as e:
            logger.error("NewPostHandler: 처리 실패: %s", e)
            raise

    async def _save_new_posts(self, posts: List[Post]) -> List[Post]:
        """신규 게시물만 저장하는 메서드 (내부 사용)"""
        try:
            saved_posts = await self.post_repo.create_posts(posts)
            logger.info("NewPostHandler: %d개 신규 게시물 저장 완료", len(saved_posts))
            logger.debug("저장된 게시물 ID 목록: %s", [post.id for post in saved_posts])
            logger.debug("저장된 게시물 요약 본문 목록: %s", [post.content_summary[:30] for post in saved_posts])
            return saved_posts
        except SQLAlchemyError as e:
            logger.error("NewPostHandler: 게시물 저장 실패: %s", e)
            raise


    async def _process_ocr_entities(self, post_picture_entites, saved_posts)-> None:
        """OCR 엔티티를 처리하는 메서드 (내부 사용)"""
        if not post_picture_entites:
            logger.info("처리할 OCR 엔티티가 없음")
        
        try:
            # saved_posts에서 post_id 매핑 생성
            post_id_mapping = {post.original_post_id: post.id for post in saved_posts}
            
            # OCR 엔티티에 post_id 설정
            for ocr_entity in post_picture_entites:
                if ocr_entity.original_post_id:
                    post_id = post_id_mapping.get(int(ocr_entity.original_post_id))
                    if post_id:
                        ocr_entity.post_id = post_id
                    else:
                        logger.warning(f"original_post_id {ocr_entity.original_post_id}에 해당하는 post_id를 찾을 수 없음")
                else:
                    logger.warning("OCR 엔티티에 original_post_id가 설정되지 않음")
            
            # Post Picture 엔티티 저장 
            saved_post_pictures = await self.post_picture_repo.create_post_pictures(post_picture_entites)
            logger.info("NewPostHandler: %d개 OCR 엔티티 저장 완료", len(saved_post_pictures))
            
            
        except Exception as e:
            logger.error("OCR 처리 중 오류 발생: %s", e)
            raise

    # async def _process_location_entities(self, location_entities, saved_posts):
    #     """Location 엔티티를 처리하는 메서드 (내부 사용)"""
    #     if not location_entities:
    #         logger.info("처리할 Location 엔티티가 없음")
    #         return []
        
    #     try:
    #         # saved_posts에서 post_id 매핑 생성
    #         post_id_mapping = {post.original_post_id: post.id for post in saved_posts}
            
    #         # Location 엔티티에 post_id 설정
    #         for location_entity in location_entities:
    #             if location_entity.original_post_id:
    #                 post_id = post_id_mapping.get(int(location_entity.original_post_id))
    #                 if post_id:
    #                     location_entity.post_id = post_id
    #                 else:
    #                     logger.warning(f"original_post_id {location_entity.original_post_id}에 해당하는 post_id를 찾을 수 없음")
    #             else:
    #                 logger.warning("Location 엔티티에 original_post_id가 설정되지 않음")
            
    #         # Location 엔티티 저장
    #         saved_locations = await self.location_repo.create_event_location_times(location_entities)
    #         logger.info("NewPostHandler: %d개 위치 정보 저장 완료", len(saved_locations))
    #         return saved_locations
            
    #     except Exception as e:
    #         logger.error("위치 정보 저장 중 오류 발생: %s", e)
    #         raise