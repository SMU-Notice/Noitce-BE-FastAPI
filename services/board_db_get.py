from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from models.post import Post


# 테스트 코드 만들기
async def get_recent_posts_by_board(db: AsyncSession, board_id: int, limit: int = 50):
    stmt = select(Post).filter(Post.board_id == board_id).order_by(desc(Post.posted_date)).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()
