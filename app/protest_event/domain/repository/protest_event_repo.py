# app/board/domain/repository/protest_event_repo.py
from abc import ABC, abstractmethod
from typing import List
from app.protest_event.domain.protest_event import ProtestEvent

class IProtestEventRepository(ABC):
  
  @abstractmethod
  async def create_protest_event(self, protest_event: ProtestEvent) -> ProtestEvent:
      """
      시위 이벤트 하나를 저장합니다.
      
      Args:
          protest_event (ProtestEvent): 저장할 시위 이벤트 도메인 객체
          
      Returns:
          ProtestEvent: 저장된 시위 이벤트 객체 (DB에서 생성된 ID 등 포함)
          
      Raises:
          Exception: 데이터베이스 저장 중 오류 발생 시
      """
      pass
  
  @abstractmethod
  async def create_protest_events(self, protest_events: List[ProtestEvent]) -> List[ProtestEvent]:
      """
      여러 개의 시위 이벤트를 배치로 저장합니다.
      
      Args:
          protest_events (List[ProtestEvent]): 저장할 시위 이벤트 도메인 객체 리스트
          
      Returns:
          List[ProtestEvent]: 저장된 시위 이벤트 객체 리스트 (DB에서 생성된 ID 등 포함)
          
      Raises:
          Exception: 데이터베이스 저장 중 오류 발생 시
      """
      pass