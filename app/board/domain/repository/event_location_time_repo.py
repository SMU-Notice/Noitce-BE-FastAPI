from abc import ABCMeta, abstractmethod
from typing import List
from app.board.domain.event_location_time import EventLocationTime

class IEventLocationTimeRepository(metaclass=ABCMeta):
    """Interface for EventLocationTime Repository"""

    @abstractmethod
    async def create_event_location_times(self, event_location_times: List[EventLocationTime]) -> None:
        """여러 개의 이벤트 장소 및 시간 정보를 저장합니다."""
        pass