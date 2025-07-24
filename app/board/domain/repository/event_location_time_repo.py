from abc import ABC, abstractmethod
from typing import List
from app.board.domain.event_location_time import EventLocationTime

# Repository Interface
class IEventLocationTimeRepository(ABC):
    
    @abstractmethod
    async def create_event_location_times(self, events: List[EventLocationTime]) -> List[EventLocationTime]:
        """여러 개의 이벤트 장소/시간 정보를 배치로 저장 (post_id가 이미 설정된 경우)"""
        pass