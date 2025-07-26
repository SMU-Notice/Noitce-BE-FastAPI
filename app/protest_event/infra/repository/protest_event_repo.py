from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.exc import SQLAlchemyError
from typing import List
from app.database.db import get_db
from app.protest_event.infra.db_model.protest_event import ProtestEvent
from app.protest_event.domain.repository.protest_event_repo import IProtestEventRepository
from app.protest_event.domain.protest_event import ProtestEvent as ProtestEventVO
import logging

logger = logging.getLogger(__name__)

class ProtestEventRepository(IProtestEventRepository):
   
   async def create_protest_event(self, protest_event: ProtestEventVO) -> ProtestEventVO:
       """
       시위 이벤트 하나를 저장합니다.
       
       Args:
           protest_event (ProtestEventVO): 저장할 시위 이벤트 도메인 객체
           
       Returns:
           ProtestEventVO: 저장된 시위 이벤트 객체 (DB에서 생성된 ID 등 포함)
           
       Raises:
           SQLAlchemyError: 데이터베이스 저장 중 오류 발생 시
           ValueError: 필수 필드가 누락된 경우
       """
       # 필수 필드 검증
       if not all([protest_event.location, protest_event.protest_date, 
                  protest_event.start_time, protest_event.end_time]):
           logger.error("Protest event with missing required fields")
           raise ValueError("All required fields (location, protest_date, start_time, end_time) must be provided")
           
       async for db in get_db():
           try:
               # 도메인 객체를 모델로 변환
               event_model = self._convert_to_model(protest_event)
               
               # DB에 추가
               db.add(event_model)
               
               # flush()로 DB에 반영하되 트랜잭션은 유지 (ID 등 자동생성 값 획득)
               await db.flush()
               
               # 저장된 모델을 VO로 변환
               saved_event_vo = self._convert_to_domain(event_model)
               
               # 최종 커밋
               await db.commit()
               
               logger.info(f"Successfully created protest event with ID: {saved_event_vo.id}")
               return saved_event_vo
               
           except SQLAlchemyError as e:
               await db.rollback()
               logger.error(f"Error creating protest event: {e}")
               raise e
   
   async def create_protest_events(self, protest_events: List[ProtestEventVO]) -> List[ProtestEventVO]:
       """
       여러 개의 시위 이벤트를 배치로 저장합니다.
       
       Args:
           protest_events (List[ProtestEventVO]): 저장할 시위 이벤트 도메인 객체 리스트
           
       Returns:
           List[ProtestEventVO]: 저장된 시위 이벤트 객체 리스트 (DB에서 생성된 ID 등 포함)
           
       Raises:
           SQLAlchemyError: 데이터베이스 저장 중 오류 발생 시
           ValueError: 필수 필드가 누락된 이벤트가 있을 때
       """
       # 필수 필드 검증
       invalid_events = [event for event in protest_events if not all([
           event.location, event.protest_date, event.start_time, event.end_time
       ])]
       if invalid_events:
           logger.warning(f"Protest events with missing required fields found: {len(invalid_events)} events. These will be skipped.")
           protest_events = [event for event in protest_events if all([
               event.location, event.protest_date, event.start_time, event.end_time
           ])]
           
       if not protest_events:
           logger.info("No valid protest events to save (all events lack required fields)")
           return []
           
       async for db in get_db():
           try:
               # 배치 변환 (빠른 리스트 컴프리헨션)
               event_models = self._convert_to_models_batch(protest_events)
               
               # 배치 추가
               db.add_all(event_models)
               
               # flush()로 DB에 반영하되 트랜잭션은 유지 (ID 등 자동생성 값 획득)
               await db.flush()
               
               # 저장된 모델들을 배치로 VO 변환
               saved_event_vos = self._convert_to_domains_batch(event_models)
               
               # 최종 커밋
               await db.commit()
               
               logger.info(f"Successfully created {len(saved_event_vos)} protest events")
               return saved_event_vos
               
           except SQLAlchemyError as e:
               await db.rollback()
               logger.error(f"Error creating protest events: {e}")
               raise e

   def _convert_to_model(self, event_vo: ProtestEventVO) -> ProtestEvent:
       """
       Domain Entity를 SQLAlchemy Model로 변환합니다.
       
       Args:
           event_vo (ProtestEventVO): 변환할 시위 이벤트 도메인 객체
           
       Returns:
           ProtestEvent: SQLAlchemy 모델 객체
       """
       return ProtestEvent(**event_vo.to_dict())

   def _convert_to_domain(self, event_model: ProtestEvent) -> ProtestEventVO:
       """
       SQLAlchemy Model을 Domain Entity로 변환합니다.
       
       Args:
           event_model (ProtestEvent): 변환할 SQLAlchemy 모델 객체
           
       Returns:
           ProtestEventVO: 시위 이벤트 도메인 객체
       """
       return ProtestEventVO.from_dict(event_model.to_dict())

   def _convert_to_models_batch(self, event_vos: List[ProtestEventVO]) -> List[ProtestEvent]:
       """
       Domain Entity를 SQLAlchemy Model로 배치 변환합니다.
       
       Args:
           event_vos (List[ProtestEventVO]): 변환할 시위 이벤트 도메인 객체 리스트
           
       Returns:
           List[ProtestEvent]: SQLAlchemy 모델 객체 리스트
       """
       return [
           ProtestEvent(**event.to_dict())
           for event in event_vos
       ]

   def _convert_to_domains_batch(self, event_models: List[ProtestEvent]) -> List[ProtestEventVO]:
       """
       SQLAlchemy Model을 Domain Entity로 배치 변환합니다.
       
       Args:
           event_models (List[ProtestEvent]): 변환할 SQLAlchemy 모델 객체 리스트
           
       Returns:
           List[ProtestEventVO]: 시위 이벤트 도메인 객체 리스트
       """
       return [
           ProtestEventVO.from_dict(model.to_dict())
           for model in event_models
       ]