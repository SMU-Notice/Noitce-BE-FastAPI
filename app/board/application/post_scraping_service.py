# domains/board/application/PostScrapingService.py
import logging
from typing import List, Dict, Tuple
from datetime import datetime
from ..domain import Post
from ..domain import PostRepository
from ..infrastructure.scrapers.models.scraped_post import ScrapedBoardData, ScrapedPost

logger = logging.getLogger(__name__)

class PostScrapingService:
    """게시물 스크래핑 결과 처리를 담당하는 Application Service"""
    
    def __init__(self, post_repository: PostRepository):
        self.post_repo = post_repository
    
    async def handle_scraped_posts(self, scraped_data: ScrapedBoardData) -> Dict[str, int]:
        """
        스크래핑된 게시물 데이터를 처리
        
        :param scraped_data: 검증된 스크래핑 데이터
        :return: 처리 결과 (신규/업데이트 개수)
        """
        logger.info(f"게시판 {scraped_data.board_id} 스크래핑 데이터 처리 시작")
        
        # 신규/기존 게시물 분류
        new_posts, existing_posts_updates = await self._classify_scraped_posts(scraped_data)
        
        # 기존 게시물 조회수 업데이트
        updated_count = 0
        if existing_posts_updates:
            logger.info(f"기존 게시물 조회수 업데이트: {len(existing_posts_updates)}개")
            updated_count = await self._update_existing_posts(existing_posts_updates)
        
        # 신규 게시물 저장
        created_count = 0
        if new_posts:
            logger.info(f"신규 게시물 저장: {len(new_posts)}개")
            created_count = await self._save_new_posts(new_posts)
        
        logger.info(f"처리 완료 - 신규: {created_count}, 업데이트: {updated_count}")
        
        return {
            "created": created_count,
            "updated": updated_count,
            "total_processed": created_count + updated_count
        }
    
    async def _classify_scraped_posts(
        self, 
        scraped_data: ScrapedBoardData
    ) -> Tuple[List[Post], List[Dict]]:
        """스크래핑된 데이터를 신규/기존으로 분류"""
        
        # DB에서 기존 게시물 조회
        existing_posts = await self.post_repo.find_recent_by_board_id(
            scraped_data.board_id, 
            scraped_data.count
        )
        
        # 기존 게시물 매핑 (original_post_id -> Post)
        existing_post_map = {
            post.original_post_id: post 
            for post in existing_posts
        }
        
        new_posts = []
        existing_updates = []
        
        for scraped_post in scraped_data.data.values():
            if scraped_post.original_post_id in existing_post_map:
                # 기존 게시물 - 조회수만 업데이트
                existing_post = existing_post_map[scraped_post.original_post_id]
                if existing_post.view_count != scraped_post.view_count:
                    existing_updates.append({
                        "post_id": existing_post.id,
                        "view_count": scraped_post.view_count
                    })
            else:
                # 신규 게시물 - Domain Entity 생성
                new_post = self._convert_to_domain_entity(scraped_post, scraped_data.board_id)
                new_posts.append(new_post)
        
        return new_posts, existing_updates
    
    async def _save_new_posts(self, new_posts: List[Post]) -> int:
        """신규 게시물들을 저장"""
        saved_posts = await self.post_repo.save_multiple(new_posts)
        return len(saved_posts)
    
    async def _update_existing_posts(self, updates: List[Dict]) -> int:
        """기존 게시물들의 조회수 업데이트"""
        for update in updates:
            await self.post_repo.update_view_count(
                update["post_id"], 
                update["view_count"]
            )
        return len(updates)
    
    def _convert_to_domain_entity(self, scraped_post: ScrapedPost, board_id: int) -> Post:
        """ScrapedPost → Domain Post Entity 변환"""
        return Post(
            board_id=board_id,
            original_post_id=scraped_post.original_post_id,
            type_=scraped_post.post_type,
            title=scraped_post.title,
            url=scraped_post.url,
            view_count=scraped_post.view_count,
            has_reference=scraped_post.has_reference,
            posted_date=scraped_post.posted_date,
            content_summary=None  # 아직 요약 없음
        )