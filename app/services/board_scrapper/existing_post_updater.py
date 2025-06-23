class ExistingPostsUpdater:
    def __init__(self, post_repo: PostRepository):
        self.post_repo = post_repo

    async def update(self, existing_posts_id_view_count: list[dict]):
        await self.post_repo.update_multiple_posts(existing_posts_id_view_count)
