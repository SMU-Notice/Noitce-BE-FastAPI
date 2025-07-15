import logging
from typing import List, Dict, Any, Tuple
from app.board.infra.repository.post_repo import PostRepository
from app.board.application.post_processor import PostProcessor
from app.board.application.dto.classification_result import ClassificationResult

logger = logging.getLogger(__name__)


class PostClassifier:
    """게시물 분류 전용 클래스 - 순수 분류만 담당"""
    
    def __init__(self, post_repo: PostRepository = None):
        self.post_repo = post_repo or PostRepository()
        self.post_processor = PostProcessor()
    
    async def classify_posts(self, scraped_posts: Dict[str, Any]) -> ClassificationResult:
        """
        크롤링된 게시물을 기존/신규로 분류
        
        Parameters:
        - scraped_posts (dict): 도메인으로 변환된 크롤링 결과
        
        Returns:
        - ClassificationResult: 분류 결과
        """
        board_id = scraped_posts["board_id"]
        scraped_count = scraped_posts["scraped_count"]
        data = scraped_posts["data"]

        logger.info("PostClassifier: 게시물 분류 시작 (board_id=%s, scraped_count=%s)", board_id, scraped_count)
        
        # DB에서 기존 게시물 조회
        existing_posts_mapping = await self._get_existing_posts_mapping(board_id, scraped_count)
        
        # 신규/기존 게시물 분류
        new_posts, existing_posts_updates = self._classify_by_original_id(data, existing_posts_mapping)
        
        result = ClassificationResult(
            new_posts=new_posts,
            existing_posts_updates=existing_posts_updates
        )
        
        logger.info("PostClassifier: 분류 완료 - 신규: %d개, 기존: %d개", 
                   len(result.new_posts), len(result.existing_posts_updates))
        
        # PostProcessor를 통해 게시물 처리
        return await self.post_processor.process_posts(result)
    
    
    async def _get_existing_posts_mapping(self, board_id: int, scraped_count: int) -> Dict[str, int]:
        """DB에서 기존 게시물 조회하여 매핑 생성"""
        posts_in_db = await self.post_repo.read_posts_desc_by_id(board_id, scraped_count)
        
        if not posts_in_db:
            logger.info("DB에 기존 게시물이 없습니다.")
            return {}
        
        mapping = {str(post.original_post_id): post.id for post in posts_in_db}
        logger.info("기존 게시물 매핑 생성 완료: %d개", len(mapping))
        
        return mapping
    
    def _classify_by_original_id(self, scraped_data: Dict[str, Any], 
                                existing_posts_mapping: Dict[str, int]) -> Tuple[List[Any], List[Dict[str, Any]]]:
        """original_post_id 기준으로 분류"""
        new_posts = []
        existing_posts_updates = []
        
        for original_post_id in reversed(scraped_data):
            post_data = scraped_data[original_post_id]  # 이미 Post 엔티티로 변환된 객체
            
            if original_post_id in existing_posts_mapping:
                # 기존 게시물 - 조회수 업데이트
                update_info = {
                    "id": existing_posts_mapping[original_post_id],
                    "view_count": post_data.view_count
                }
                existing_posts_updates.append(update_info)
                logger.debug("기존 게시물 업데이트 대상: original_post_id=%s", original_post_id)
            else:
                # 신규 게시물 - 이미 변환된 Post 객체 그대로 사용
                new_posts.append(post_data)
                logger.info("신규 게시물: original_post_id=%s, title=%s", 
                           original_post_id, post_data.title)
        
        return new_posts, existing_posts_updates