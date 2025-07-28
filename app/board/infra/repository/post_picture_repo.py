from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from typing import List
from app.database.db import get_db
from app.board.infra.db_models.post_picture import PostPicture as PostPictureModel
from app.board.domain.repository.post_picture_repo import IPostPictureRepository
from app.board.domain.post_picture import PostPicture
from app.board.infra.schemas.post_picture_schema import PostPictureSchema
import logging

logger = logging.getLogger(__name__)


class PostPictureRepository(IPostPictureRepository):
    
    async def create_post_picture(self, picture: PostPicture) -> PostPicture:
        """
        게시글 사진 정보를 저장합니다.
        
        Args:
            picture (PostPicture): 저장할 게시글 사진 도메인 객체 (post_id가 이미 설정되어 있어야 함)
            
        Returns:
            PostPicture: 저장된 게시글 사진 객체 (DB에서 생성된 ID 등 포함)
            
        Raises:
            SQLAlchemyError: 데이터베이스 저장 중 오류 발생 시
            ValueError: post_id가 설정되지 않은 경우
        """
        if not picture.post_id:
            raise ValueError("post_id is required for creating post picture")
            
        async for db in get_db():
            try:
                # Domain Entity를 SQLAlchemy Model로 변환
                picture_model = PostPictureModel(**picture.to_dict())
                
                # DB에 추가
                db.add(picture_model)
                
                # flush()로 DB에 반영하되 트랜잭션은 유지 (ID 등 자동생성 값 획득)
                await db.flush()
                
                # Pydantic Schema를 통한 자동 변환
                schema_data = PostPictureSchema.from_orm(picture_model).dict()
                schema_data['original_post_id'] = picture.original_post_id  # 원본 데이터 추가
                schema_data['original_ocr_text'] = picture.original_ocr_text
                
                saved_picture = PostPicture.from_dict(schema_data)
                
                # 최종 커밋
                await db.commit()
                
                return saved_picture
                
            except SQLAlchemyError as e:
                await db.rollback()
                raise e

    async def create_post_pictures(self, pictures: List[PostPicture]) -> List[PostPicture]:
        """
        여러 게시글 사진 정보를 일괄 저장합니다.
        
        Args:
            pictures (List[PostPicture]): 저장할 게시글 사진 도메인 객체 리스트 (각각 post_id가 설정되어 있어야 함)
            
        Returns:
            List[PostPicture]: 저장된 게시글 사진 객체 리스트 (DB에서 생성된 ID 등 포함)
            
        Raises:
            SQLAlchemyError: 데이터베이스 저장 중 오류 발생 시
            ValueError: post_id가 설정되지 않은 사진이 있는 경우
        """
        if not pictures:
            return []
            
        # post_id 검증
        for i, picture in enumerate(pictures):
            if not picture.post_id:
                raise ValueError(f"post_id is required for creating post picture at index {i}")
        
        async for db in get_db():
            try:
                # Domain Entity를 SQLAlchemy Model로 변환
                picture_models = [PostPictureModel(**picture.to_dict()) for picture in pictures]
                
                # DB에 일괄 추가
                db.add_all(picture_models)
                
                # flush()로 DB에 반영하되 트랜잭션은 유지 (ID 등 자동생성 값 획득)
                await db.flush()
                
                # Pydantic Schema를 통한 자동 변환
                saved_pictures = []
                for i, model in enumerate(picture_models):
                    saved_pictures.append(PostPicture.from_dict({
                        'id': model.__dict__.get('id'),
                        'post_id': model.__dict__.get('post_id'),
                        'url': model.__dict__.get('url', ''),
                        'picture_summary': model.__dict__.get('picture_summary', ''),
                        'created_at': model.__dict__.get('created_at'),
                        'original_post_id': pictures[i].original_post_id,
                        'original_ocr_text': pictures[i].original_ocr_text
                    }))
                
                # 최종 커밋
                await db.commit()
                
                logger.info(f"PostPictureRepository: {len(saved_pictures)}개 게시글 사진 저장 완료")
                return saved_pictures
                
            except SQLAlchemyError as e:
                await db.rollback()
                logger.error(f"PostPictureRepository: 게시글 사진 일괄 저장 실패: {e}")
                raise e