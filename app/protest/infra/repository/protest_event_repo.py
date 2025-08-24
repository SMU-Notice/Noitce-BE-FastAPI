from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.exc import SQLAlchemyError
from typing import List
from app.database.db import get_db
from app.protest.infra.db_model.protest_event import ProtestEvent
from app.protest.domain.repository.protest_event_repo import IProtestEventRepository
from app.protest.domain.protest_event import ProtestEvent as ProtestEventVO
import logging

logger = logging.getLogger(__name__)

class ProtestEventRepository(IProtestEventRepository):
    
    async def create_protest_events(self, protest_events: List[ProtestEventVO]) -> List[ProtestEventVO]:
        """
        여러 개의 시위 이벤트를 저장합니다.
        
        Args:
            protest_events (List[ProtestEventVO]): 저장할 시위 이벤트 도메인 객체 리스트
            
        Returns:
            List[ProtestEventVO]: 저장된 시위 이벤트 객체 리스트 (DB에서 생성된 ID 등 포함)
            
        Raises:
            SQLAlchemyError: 데이터베이스 저장 중 오류 발생 시
            ValueError: 필수 필드가 누락된 경우
        """
        if not protest_events:
            logger.warning("Empty protest events list provided")
            raise ValueError("Protest events list cannot be empty")
            
        async for db in get_db():
            try:
                # 도메인 객체들을 SQLAlchemy 모델로 변환
                db_models = []
                for event in protest_events:
                    # 필수 필드 검증
                    if not all([event.location, event.protest_date, 
                              event.start_time, event.end_time]):
                        logger.error("Protest event with missing required fields")
                        raise ValueError("All required fields (location, protest_date, start_time, end_time) must be provided")
                    
                    db_model = ProtestEvent(
                        location=event.location,
                        protest_date=event.protest_date,
                        start_time=event.start_time,
                        end_time=event.end_time
                    )
                    db_models.append(db_model)
                
                # DB에 추가
                db.add_all(db_models)
                
                # flush()로 DB에 반영하되 트랜잭션은 유지 (ID 등 자동생성 값 획득)
                await db.flush()
                
                # SQLAlchemy 모델을 도메인 객체로 변환
                result = []
                for db_model in db_models:
                    domain_obj = ProtestEventVO(
                        id=db_model.id,
                        location=db_model.location,
                        protest_date=db_model.protest_date,
                        start_time=db_model.start_time,
                        end_time=db_model.end_time
                    )
                    result.append(domain_obj)
                
                # 최종 커밋
                await db.commit()
                
                logger.info(f"Successfully created {len(result)} protest events")
                return result
                
            except SQLAlchemyError as e:
                await db.rollback()
                logger.error(f"Error creating protest events: {e}")
                raise e
            except Exception as e:
                await db.rollback()
                logger.error(f"Unexpected error creating protest events: {e}")
                raise e