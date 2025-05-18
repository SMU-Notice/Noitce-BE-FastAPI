import logging
from app.models.post import Post
from app.database.db import get_db
from app.repository.post_respository import PostRepository
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

async def handle_scraped_posts(scraped_posts: dict) -> dict:
    logger.info("handle_scraped_posts: 시작")
    new_posts = []
    existing_posts_id_view_count = []

    async for session in get_db():
        post_repo = PostRepository(session)
        board_id = scraped_posts["board_id"]
        count = scraped_posts["count"]
        data = scraped_posts["data"]

        logger.info("DB에서 기존 게시물 조회 (board_id=%s, count=%s)", board_id, count)
        posts_in_db = await post_repo.read_posts_desc_by_id(board_id, count)

        db_post_dict = {str(post.original_post_id): post.id for post in posts_in_db} if posts_in_db else {}

        for article_id in reversed(data):
            scraped_post_data = data[article_id]

            if article_id in db_post_dict:
                existing_posts_id_view_count.append({
                    "id": db_post_dict[article_id],
                    "view_count": int(scraped_post_data["view_count"])
                })
                # logger.info("기존 게시물 업데이트 대상: id=%s, view_count=%s", db_post_dict[article_id], scraped_post_data["view_count"])
            else:
                new_post = Post(
                    board_id=board_id,
                    original_post_id=int(article_id),
                    type_=scraped_post_data["post_type"],
                    title=scraped_post_data["title"],
                    content_summary="N/A",
                    view_count=int(scraped_post_data["view_count"]),
                    url=scraped_post_data["url"],
                    has_reference=scraped_post_data["has_reference"],
                    posted_date=datetime.strptime(scraped_post_data["date"], "%Y-%m-%d").date()
                )
                new_posts.append(new_post)
                logger.info("신규 게시물 추가 대상: original_post_id=%s, title=%s", article_id, scraped_post_data["title"])

        # 업데이트 & 저장
        if existing_posts_id_view_count:
            logger.info("기존 게시물 조회수 업데이트 시작, 대상 개수: %d", len(existing_posts_id_view_count))
            await post_repo.update_multiple_posts(existing_posts_id_view_count)

        if new_posts:
            logger.info("신규 게시물 DB 저장 시작, 대상 개수: %d", len(new_posts))
            await post_repo.create_posts(new_posts)

    logger.info("handle_scraped_posts: 완료, 신규 게시물 개수=%d", len(new_posts))
    return new_posts
