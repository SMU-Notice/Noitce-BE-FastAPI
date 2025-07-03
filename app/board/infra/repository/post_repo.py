from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from typing import List
from datetime import datetime

from app.board.domain.post import Post as PostVO
from app.board.infra.db_models.post import Post
from app.board.domain.repository.post_repo import IPostRepository
from app.database.db import get_db


class PostRepository(IPostRepository):
    
    async def create_posts(self, posts: List[PostVO]) -> List[PostVO]:
        """
        여러 개의 게시글을 배치로 저장하고 저장된 데이터를 반환합니다.
        
        Args:
            posts (List[PostVO]): 저장할 게시글 도메인 객체 리스트
            
        Returns:
            List[PostVO]: 저장된 게시글 객체 리스트 (DB에서 생성된 ID 등 포함)
            
        Raises:
            SQLAlchemyError: 데이터베이스 저장 중 오류 발생 시
        """
        async for db in get_db():
            try:
                # 배치 변환 (빠른 리스트 컴프리헨션)
                post_models = self._convert_to_models_batch(posts)
                
                # 배치 추가
                db.add_all(post_models)
                
                # flush()로 DB에 반영하되 트랜잭션은 유지 (ID 등 자동생성 값 획득)
                await db.flush()
                
                # 저장된 모델들을 배치로 VO 변환
                saved_post_vos = self._convert_to_domains_batch(post_models)
                
                # 최종 커밋
                await db.commit()
                
                return saved_post_vos
                
            except SQLAlchemyError as e:
                await db.rollback()
                raise e

    async def read_posts_desc_by_id(self, board_id: int, record_count: int) -> List[PostVO]:
        """
        특정 게시판의 게시글을 최신순으로 조회합니다.
        
        Args:
            board_id (int): 조회할 게시판 ID
            record_count (int): 조회할 게시글 개수 (LIMIT)
            
        Returns:
            List[PostVO]: 조회된 게시글 도메인 객체 리스트 (최신순)
            
        Raises:
            SQLAlchemyError: 데이터베이스 조회 중 오류 발생 시
        """
        async for db in get_db():
            try:
                result = await db.execute(
                    select(Post)
                    .where(Post.board_id == board_id)
                    .order_by(Post.id.desc())
                    .limit(record_count)
                )
                post_models = result.scalars().all()
                
                # 배치 변환 (빠른 리스트 컴프리헨션)
                return self._convert_to_domains_batch(post_models)
                
            except SQLAlchemyError as e:
                raise e

    async def update_multiple_posts(self, updates: List[dict]) -> None:
        """
        여러 게시글의 특정 필드를 배치로 업데이트합니다.
        
        Args:
            updates (List[dict]): 업데이트할 게시글 정보 리스트
                                 각 dict는 {"id": int, "field1": value1, "field2": value2, ...} 형태
                                 예: [{"id": 1, "view_count": 100}, {"id": 2, "view_count": 150}]
                                 
        Raises:
            SQLAlchemyError: 데이터베이스 업데이트 중 오류 발생 시
        """
        async for db in get_db():
            try:
                for update_data in updates:
                    post_id = update_data.pop("id")
                    await db.execute(
                        update(Post).where(Post.id == post_id).values(**update_data)
                    )
                await db.commit()
            except SQLAlchemyError as e:
                await db.rollback()
                raise e

    def _convert_to_models_batch(self, post_vos: List[PostVO]) -> List[Post]:
        """
        Domain Entity를 SQLAlchemy Model로 배치 변환합니다.
        
        Args:
            post_vos (List[PostVO]): 변환할 게시글 도메인 객체 리스트
            
        Returns:
            List[Post]: SQLAlchemy 모델 객체 리스트
        """
        return [
            Post(
                id=vo.id,
                board_id=vo.board_id,
                original_post_id=vo.original_post_id,
                type_=vo.post_type,
                title=vo.title,
                content_summary=vo.content_summary,
                view_count=vo.view_count,
                url=vo.url,
                has_reference=vo.has_reference,
                posted_date=vo.posted_date,
                scraped_at=datetime.now() 
            ) for vo in post_vos
        ]

    def _convert_to_domains_batch(self, post_models: List[Post]) -> List[PostVO]:
        """
        SQLAlchemy Model을 Domain Entity로 배치 변환합니다.
        
        Args:
            post_models (List[Post]): 변환할 SQLAlchemy 모델 객체 리스트
            
        Returns:
            List[PostVO]: 게시글 도메인 객체 리스트
        """
        return [
            PostVO(
                id=m.id,
                board_id=m.board_id,
                original_post_id=m.original_post_id,
                post_type=m.type_,
                title=m.title,
                content_summary=m.content_summary,
                view_count=m.view_count,
                url=m.url,
                has_reference=m.has_reference,
                posted_date=m.posted_date,
            ) for m in post_models
        ]