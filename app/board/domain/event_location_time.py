from datetime import date, time, datetime
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class EventLocationTime:
    """이벤트 장소 및 시간 정보"""
    id: Optional[int] = None
    post_id: Optional[int] = None
    location: str = ""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    
    @classmethod
    def from_model(cls, model) -> 'EventLocationTime':
        """
        SQLAlchemy Model에서 Domain Entity로 변환
        
        Args:
            model: SQLAlchemy 모델 객체
            
        Returns:
            EventLocationTime: 도메인 엔티티
        """
        return cls(
            id=model.id,
            location=model.location,
            start_date=model.start_date,
            end_date=model.end_date,
            start_time=model.start_time,
            end_time=model.end_time
        )
    
    def to_model(self, model_class):
        """
        Domain Entity에서 SQLAlchemy Model로 변환
        
        Args:
            model_class: SQLAlchemy 모델 클래스
            
        Returns:
            SQLAlchemy 모델 객체
        """
        return model_class(
            id=self.id,
            location=self.location,
            start_date=self.start_date,
            end_date=self.end_date,
            start_time=self.start_time,
            end_time=self.end_time,
            created_at=datetime.now()
        )
    
    @classmethod
    def from_models_batch(cls, models: List) -> List['EventLocationTime']:
        """
        SQLAlchemy Model 리스트에서 Domain Entity 리스트로 배치 변환
        
        Args:
            models: SQLAlchemy 모델 객체 리스트
            
        Returns:
            List[EventLocationTime]: 도메인 엔티티 리스트
        """
        return [cls.from_model(model) for model in models]
    
    @classmethod
    def to_models_batch(cls, entities: List['EventLocationTime'], model_class) -> List:
        """
        Domain Entity 리스트에서 SQLAlchemy Model 리스트로 배치 변환
        
        Args:
            entities: 도메인 엔티티 리스트
            model_class: SQLAlchemy 모델 클래스
            
        Returns:
            List: SQLAlchemy 모델 객체 리스트
        """
        return [entity.to_model(model_class) for entity in entities]
    

# 사용 예시
if __name__ == "__main__":
    # 1. OpenAI 응답에서 생성
    openai_response = {
        "장소": "상명대학교 제1공학관",
        "시작_날짜": "2025-07-20",
        "종료_날짜": "2025-07-25",
        "시작_시각": "09:00",
        "종료_시각": "18:00"
    }
    
    event = EventLocationTime.from_openai_response(openai_response)
    print(f"이벤트 정보: {event}")
    print(f"유효한 정보: {event.is_valid()}")
    
    # 2. 모델 변환 (예시)
    class EventModel:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    # 엔티티 → 모델
    model = event.to_model(EventModel)
    print(f"모델 객체: {model.location}")
    
    # 모델 → 엔티티
    event2 = EventLocationTime.from_model(model)
    print(f"다시 변환된 엔티티: {event2}")
    
    # 3. 배치 변환
    events = [event, event2]
    models = EventLocationTime.to_models_batch(events, EventModel)
    print(f"배치 변환된 모델 수: {len(models)}")
    
    events_back = EventLocationTime.from_models_batch(models)
    print(f"배치 변환된 엔티티 수: {len(events_back)}")