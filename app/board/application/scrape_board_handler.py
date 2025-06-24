import logging
from app.board.infra.repository.post_repo import PostRepository
from app.board.domain.post import Post
from datetime import datetime, timezone
from typing import Tuple


logger = logging.getLogger(__name__)

class ScrapedPostHandler:
    def __init__(self):
        self.post_repo = PostRepository()

    async def handleScrapedPosts(self, scraped_posts: dict) -> dict:
        logger.info("handle_scraped_posts: 시작")
        new_posts, existing_posts_id_and_view_count = await self.classify(scraped_posts)

        if existing_posts_id_and_view_count:
            logger.info("기존 게시물 조회수 업데이트 시작, 대상 개수: %d", len(existing_posts_id_and_view_count))
            await self.post_repo.update_multiple_posts(existing_posts_id_and_view_count)

        if new_posts:
            logger.info("신규 게시물 DB 저장 시작, 대상 개수: %d", len(new_posts))
            await self.post_repo.create_posts(new_posts)

        logger.info("handle_scraped_posts: 완료, 신규 게시물 개수=%d", len(new_posts))
        return new_posts

    async def classify(self, scraped_posts: dict) -> Tuple[list, list]:
        """
        크롤링된 게시물 데이터를 기반으로, DB에 이미 존재하는 게시물과 신규 게시물을 분류합니다.

        Parameters:
        - scraped_posts (dict): 크롤링 결과. 예시 구조:
            {
                "board_id": int,
                "count": int,
                "data": {
                    "article_id1": {
                        "post_type": str,
                        "title": str,
                        "view_count": str,
                        "url": str,
                        "has_reference": bool,
                        "date": "YYYY-MM-DD"
                    },
                    ...
                }
            }

        Returns:
        - Tuple[list[Post], list[dict]]: 
            - 첫 번째 리스트는 DB에 존재하지 않아 새로 저장해야 할 Post 객체 목록
            - 두 번째 리스트는 이미 DB에 존재하며 조회수만 업데이트할 게시물 정보 목록 (dict 형식: {"id": int, "view_count": int})
        """
        board_id = scraped_posts["board_id"]
        count = scraped_posts["count"]
        data = scraped_posts["data"]

        logger.info("DB에서 기존 게시물 조회 (board_id=%s, count=%s)", board_id, count)
        posts_in_db = await self.post_repo.read_posts_desc_by_id(board_id, count)

        # 기존 게시물 original_post_id -> DB id 매핑
        db_post_dict = {str(post.original_post_id): post.id for post in posts_in_db} if posts_in_db else {}

        new_posts = []
        existing_posts_id_and_view_count = []

        for original_post_id in reversed(data):  # 최신 게시물이 먼저 처리되도록 역순
            scraped_post_data = data[original_post_id]

            if original_post_id in db_post_dict:
                # 이미 존재하는 게시물: view_count만 업데이트
                existing_posts_id_and_view_count.append({
                    "id": db_post_dict[original_post_id],
                    "view_count": scraped_post_data.view_count  
                })
            else:
                # 신규 게시물 생성
                new_post = scraped_post_data
                new_posts.append(new_post)
                logger.info("신규 게시물 추가 대상: original_post_id=%s, title=%s", original_post_id, scraped_post_data.title)

        return new_posts, existing_posts_id_and_view_count

