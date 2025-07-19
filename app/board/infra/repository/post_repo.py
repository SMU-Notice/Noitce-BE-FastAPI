from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, text
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
            

    async def update_posts_batch(self, posts: List[PostVO]) -> None:
            """
            여러 게시글을 배치로 업데이트합니다.
            
            Args:
                posts (List[PostVO]): 업데이트할 게시글 객체 리스트 (id 포함)
                
            Raises:
                SQLAlchemyError: 데이터베이스 업데이트 중 오류 발생 시
            """
            if not posts:
                return
                
            async for db in get_db():
                try:
                    current_time = datetime.now()
                    
                    # MySQL CASE WHEN을 사용한 배치 업데이트
                    post_ids = [post.id for post in posts]
                    
                    # 각 필드별로 CASE WHEN 구문 생성
                    title_cases = []
                    content_summary_cases = []
                    view_count_cases = []
                    url_cases = []
                    has_reference_cases = []
                    posted_date_cases = []
                    
                    params = {}
                    for i, post in enumerate(posts):
                        title_cases.append(f"WHEN id = :id_{i} THEN :title_{i}")
                        content_summary_cases.append(f"WHEN id = :id_{i} THEN :content_summary_{i}")
                        view_count_cases.append(f"WHEN id = :id_{i} THEN :view_count_{i}")
                        url_cases.append(f"WHEN id = :id_{i} THEN :url_{i}")
                        has_reference_cases.append(f"WHEN id = :id_{i} THEN :has_reference_{i}")
                        posted_date_cases.append(f"WHEN id = :id_{i} THEN :posted_date_{i}")
                        
                        params.update({
                            f'id_{i}': post.id,
                            f'title_{i}': post.title,
                            f'content_summary_{i}': post.content_summary,
                            f'view_count_{i}': post.view_count,
                            f'url_{i}': post.url,
                            f'has_reference_{i}': post.has_reference,
                            f'posted_date_{i}': post.posted_date,
                        })
                    
                    # 배치 업데이트 쿼리 생성
                    batch_update_query = text(f"""
                        UPDATE posts SET
                            title = CASE {' '.join(title_cases)} END,
                            content_summary = CASE {' '.join(content_summary_cases)} END,
                            view_count = CASE {' '.join(view_count_cases)} END,
                            url = CASE {' '.join(url_cases)} END,
                            has_reference = CASE {' '.join(has_reference_cases)} END,
                            posted_date = CASE {' '.join(posted_date_cases)} END,
                            scraped_at = :scraped_at
                        WHERE id IN ({','.join([f':id_{i}' for i in range(len(posts))])})
                    """)
                    
                    params['scraped_at'] = current_time
                    
                    await db.execute(batch_update_query, params)
                    await db.commit()
                    
                except SQLAlchemyError as e:
                    await db.rollback()
                    raise e


    # 더 간단한 버전 (SQLAlchemy bulk_update_mappings 사용)
    async def update_posts_batch_simple(self, posts: List[PostVO]) -> None:
        """
        SQLAlchemy bulk_update_mappings를 사용한 배치 업데이트
        
        Args:
            posts (List[PostVO]): 업데이트할 게시글 객체 리스트 (id 포함)
        """
        if not posts:
            return
            
        async for db in get_db():
            try:
                current_time = datetime.now()
                
                # 업데이트 데이터 준비
                update_mappings = []
                for post in posts:
                    update_mappings.append({
                        'id': post.id,
                        'title': post.title,
                        'content_summary': post.content_summary,
                        'view_count': post.view_count,
                        'url': post.url,
                        'has_reference': post.has_reference,
                        'posted_date': post.posted_date,
                        'scraped_at': current_time
                    })
                
                # SQLAlchemy bulk_update_mappings 사용
                await db.run_sync(
                    lambda sync_session: sync_session.bulk_update_mappings(
                        Post, update_mappings
                    )
                )
                await db.commit()
                
            except SQLAlchemyError as e:
                await db.rollback()
                raise e

    async def find_by_original_ids(self, board_id: int, original_ids: List[str]) -> List[PostVO]:
        """
        특정 게시판에서 original_id 리스트에 해당하는 게시물들을 조회합니다.
        
        Args:
            board_id: 게시판 ID
            original_ids: 조회할 original_post_id 리스트
            
        Returns:
            해당하는 게시물들의 목록
        """
        if not original_ids:
            return []
            
        async for db in get_db():
            try:
                # 문자열 original_ids를 정수로 변환
                original_ids_int = [int(oid) for oid in original_ids]
                
                result = await db.execute(
                    select(Post)
                    .where(Post.board_id == board_id)
                    .where(Post.original_post_id.in_(original_ids_int))
                )
                post_models = result.scalars().all()
                
                return self._convert_to_domains_batch(post_models)
                
            except SQLAlchemyError as e:
                raise e

    async def upsert_posts_and_return_new(self, posts: List[PostVO]) -> List[PostVO]:
        """
        게시글들을 upsert하고 새로 생성된 게시글들만 반환합니다.
        
        Args:
            posts: upsert할 게시글 목록
            
        Returns:
            새로 생성된 게시글들의 목록 (기존에 존재하던 게시글은 제외)
        """
        if not posts:
            return []
            
        async for db in get_db():
            try:
                # 1. 기존 게시글들의 original_post_id 조회
                board_id = posts[0].board_id  # 모든 posts는 같은 board_id를 가져야 함
                original_ids = [post.original_post_id for post in posts]
                
                existing_result = await db.execute(
                    select(Post.original_post_id)
                    .where(Post.board_id == board_id)
                    .where(Post.original_post_id.in_(original_ids))
                )
                existing_original_ids = {row[0] for row in existing_result}
                
                # 2. 새로운 게시글들만 필터링
                new_posts = [post for post in posts if post.original_post_id not in existing_original_ids]
                
                if not new_posts:
                    return []
                
                # 3. 새로운 게시글들만 저장
                new_post_models = self._convert_to_models_batch(new_posts)
                db.add_all(new_post_models)
                
                # flush()로 DB에 반영하되 트랜잭션은 유지 (ID 등 자동생성 값 획득)
                await db.flush()
                
                # 저장된 모델들을 배치로 VO 변환
                saved_post_vos = self._convert_to_domains_batch(new_post_models)
                
                # 최종 커밋
                await db.commit()
                
                return saved_post_vos
                
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
    
    