from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.exc import SQLAlchemyError
from typing import List
from app.database.db import get_db
from app.board.infra.db_models.event_location_time import EventLocationTime
from app.board.infra.db_models.post import Post
from app.board.domain.repository.event_location_time_repo import IEventLocationTimeRepository
from app.board.domain.event_location_time import EventLocationTime as EventLocationTimeVO
import logging

logger = logging.getLogger(__name__)

class EventLocationTimeRepository(IEventLocationTimeRepository):
    
    async def create_event_location_times(self, events: List[EventLocationTimeVO]) -> List[EventLocationTimeVO]:
        """
        여러 개의 이벤트 장소/시간 정보를 배치로 저장합니다.
        
        Args:
            events (List[EventLocationTimeVO]): 저장할 이벤트 도메인 객체 리스트 (post_id가 이미 설정되어 있어야 함)
            
        Returns:
            List[EventLocationTimeVO]: 저장된 이벤트 객체 리스트 (DB에서 생성된 ID 등 포함)
            
        Raises:
            SQLAlchemyError: 데이터베이스 저장 중 오류 발생 시
            ValueError: post_id가 설정되지 않은 이벤트가 있을 때
        """
        # post_id가 설정되지 않은 이벤트 확인
        invalid_events = [event for event in events if not event.post_id]
        if invalid_events:
            logger.warning(f"Events without post_id found: {len(invalid_events)} events. These will be skipped.")
            # post_id가 없는 이벤트는 제외하고 진행
            events = [event for event in events if event.post_id]
            
        if not events:
            logger.info("No valid events to save (all events lack post_id)")
            return []
            
        async for db in get_db():
            try:
                # 배치 변환 (빠른 리스트 컴프리헨션)
                event_models = self._convert_to_models_batch(events)
                
                # 배치 추가
                db.add_all(event_models)
                
                # flush()로 DB에 반영하되 트랜잭션은 유지 (ID 등 자동생성 값 획득)
                await db.flush()
                
                # 저장된 모델들을 배치로 VO 변환
                saved_event_vos = self._convert_to_domains_batch(event_models)
                
                # 최종 커밋
                await db.commit()
                
                return saved_event_vos
                
            except SQLAlchemyError as e:
                await db.rollback()
                raise e

    def _convert_to_models_batch(self, event_vos: List[EventLocationTimeVO]) -> List[EventLocationTime]:
        """
        Domain Entity를 SQLAlchemy Model로 배치 변환합니다.
        
        Args:
            event_vos (List[EventLocationTimeVO]): 변환할 이벤트 도메인 객체 리스트
            
        Returns:
            List[EventLocationTime]: SQLAlchemy 모델 객체 리스트
        """
        return [
            EventLocationTime(**event.to_dict())
            for event in event_vos
        ]

    def _convert_to_domains_batch(self, event_models: List[EventLocationTime]) -> List[EventLocationTimeVO]:
        """
        SQLAlchemy Model을 Domain Entity로 배치 변환합니다.
        
        Args:
            event_models (List[EventLocationTime]): 변환할 SQLAlchemy 모델 객체 리스트
            
        Returns:
            List[EventLocationTimeVO]: 이벤트 도메인 객체 리스트
        """
        return [
        EventLocationTimeVO.from_dict(model.to_dict())
        for model in event_models
        ]