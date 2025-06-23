from app.models.post import Post
from app.database.db import get_db
from app.repository.post_respository import PostRepository
from datetime import datetime

class ScrapedPostService:
    async def process_scraped_posts(self, scraped_posts: dict) -> dict:
        new_posts = []
        existing_posts_id_view_count = []

        async for session in get_db():
            post_repo = PostRepository(session)
            board_id = scraped_posts["board_id"]
            count = scraped_posts["count"]
            data = scraped_posts["data"]

            # DB에서 기존 게시물 조회
            posts_in_db = await post_repo.read_posts_desc_by_id(board_id, count)
            db_post_dict = {str(post.original_post_id): post.id for post in posts_in_db} if posts_in_db else {}

            for article_id in reversed(data):
                scraped_post_data = data[article_id]

                if article_id in db_post_dict:
                    existing_posts_id_view_count.append({
                        "id": db_post_dict[article_id],
                        "view_count": int(scraped_post_data["view_count"])
                    })
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

            # 3, 4번 객체 호출
            # if existing_posts_id_view_count:
            #     await ExistingPostsUpdater(post_repo).update(existing_posts_id_view_count)
            # if new_posts:
            #     await NewPostsCreator(post_repo).create(new_posts)

        return {
            "new_posts": new_posts
        }
