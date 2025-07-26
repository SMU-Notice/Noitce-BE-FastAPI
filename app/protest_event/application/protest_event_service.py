# app/board/application/protest_event_service.py
from typing import List
from app.protest_event.domain.protest_event import ProtestEvent
from app.protest_event.domain.repository.protest_event_repo import IProtestEventRepository
import logging

logger = logging.getLogger(__name__)

class ProtestEventService:
   
   def __init__(self, protest_event_repository: IProtestEventRepository):
       self.protest_event_repository = protest_event_repository
   
   async def create_protest_events(self, protest_events: List[ProtestEvent]) -> List[ProtestEvent]:
       """
       여러 개의 시위 이벤트를 생성합니다.
       
       Args:
           protest_events (List[ProtestEvent]): 생성할 시위 이벤트 리스트
           
       Returns:
           List[ProtestEvent]: 생성된 시위 이벤트 리스트 (ID 포함)
           
       Raises:
           ValueError: 빈 리스트가 전달된 경우
           Exception: 데이터베이스 저장 중 오류 발생 시
       """
       if not protest_events:
           logger.warning("Empty protest events list provided")
           raise ValueError("Protest events list cannot be empty")
       
       logger.info(f"Creating {len(protest_events)} protest events")
       
       try:
           # Repository를 통해 저장
           created_events = await self.protest_event_repository.create_protest_events(protest_events)
           
           logger.info(f"Successfully created {len(created_events)} protest events")
           return created_events
           
       except Exception as e:
           logger.error(f"Failed to create protest events: {e}")
           raise e