# src/app/repositories/post_repository.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from app.models.post import Post
from typing import List


class PostRepository:
    def __init__(self, db: AsyncSession):
        """
        PostRepository 초기화

        :param db: 비동기 SQLAlchemy 세션
        """
        self.db = db

    async def create_post(self, post_data: dict) -> Post:
        """
        새 게시글을 생성합니다.

        :param post_data: Post 모델의 필드와 매핑되는 딕셔너리 (예: {"title": "제목", "content": "내용", ...})
        :return: 생성된 Post 객체
        :raises SQLAlchemyError: DB 작업 실패 시 예외 발생
        """
        try:
            new_post = Post(**post_data)
            self.db.add(new_post)
            await self.db.commit()
            await self.db.refresh(new_post)
            return new_post
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise e

    async def create_posts(self, posts: List[Post]) -> None:
        """
        여러 개의 게시글을 저장합니다.

        :param posts: Post 객체의 리스트
        :return: 없음
        :raises SQLAlchemyError: DB 작업 실패 시 예외 발생
        """
        try:
            for post in posts:
                self.db.add(post)
            await self.db.commit()
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise e

    async def read_posts_by_id_asc(self, record_count: int) -> List[Post]:
        """
        게시글을 ID 기준 오름차순으로 record_count개 조회합니다.

        :param record_count: 조회할 게시글 개수
        :return: 조회된 Post 객체 리스트
        :raises SQLAlchemyError: DB 작업 실패 시 예외 발생
        """
        try:
            result = await self.db.execute(
                select(Post).order_by(Post.id.asc()).limit(record_count)
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            raise e

    async def read_posts_desc_by_id(self, board_id: int, record_count: int) -> List[Post]:
        """
        특정 게시판(board_id)의 게시글을 ID 기준 내림차순으로 record_count개 조회합니다.

        :param board_id: 게시판 ID
        :param record_count: 조회할 게시글 개수
        :return: 조회된 Post 객체 리스트
        :raises SQLAlchemyError: DB 작업 실패 시 예외 발생
        """
        try:
            result = await self.db.execute(
                select(Post)
                .where(Post.board_id == board_id)
                .order_by(Post.id.desc())
                .limit(record_count)
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            raise e

    async def update_multiple_posts(self, updates: List[dict]) -> None:
        """
        여러 게시글의 일부 필드를 업데이트합니다.

        :param updates: 각 게시글의 id와 수정할 필드를 포함하는 딕셔너리 리스트  
            예: [{"id": 1, "title": "새 제목1"}, {"id": 2, "title": "새 제목2"}]
        :return: 없음
        :raises SQLAlchemyError: DB 작업 실패 시 예외 발생
        """
        try:
            for update_data in updates:
                post_id = update_data.pop("id")
                await self.db.execute(
                    update(Post).where(Post.id == post_id).values(**update_data)
                )
            await self.db.commit()
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise e
