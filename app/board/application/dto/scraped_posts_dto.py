from dataclasses import dataclass
from typing import Dict, Any
from datetime import datetime
from app.board.infra.scraper.models.scraped_post import ScrapedPost


@dataclass
class ScrapedPostsDto:
    """
    스크래핑된 게시물 데이터를 담는 DTO 클래스
    """
    board_id: int
    scraped_count: int
    data: Dict[str, ScrapedPost]
    scraped_at: datetime = None
    
    def __post_init__(self):
        """초기화 후 자동 설정"""
        if self.scraped_at is None:
            self.scraped_at = datetime.now()
        
        # scraped_count와 실제 데이터 개수 검증
        if self.scraped_count != len(self.data):
            raise ValueError(f"scraped_count({self.scraped_count})와 실제 데이터 개수({len(self.data)})가 일치하지 않습니다.")
    
    @classmethod
    def create(cls, board_id: int, scraped_posts: Dict[str, ScrapedPost]) -> 'ScrapedPostsDto':
        """
        ScrapedPostsDto 인스턴스를 생성하는 팩토리 메서드
        
        Parameters:
        - board_id: 게시판 ID
        - scraped_posts: 스크래핑된 게시물 딕셔너리
        
        Returns:
        - ScrapedPostsDto 인스턴스
        """
        return cls(
            board_id=board_id,
            scraped_count=len(scraped_posts),
            data=scraped_posts
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        딕셔너리 형태로 변환 (기존 코드와의 호환성을 위해)
        
        Returns:
        - Dict 형태의 스크래핑 데이터
        """
        return {
            "board_id": self.board_id,
            "scraped_count": self.scraped_count,
            "data": self.data,
            "scraped_at": self.scraped_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScrapedPostsDto':
        """
        딕셔너리에서 ScrapedPostsDto 생성
        
        Parameters:
        - data: 딕셔너리 형태의 스크래핑 데이터
        
        Returns:
        - ScrapedPostsDto 인스턴스
        """
        return cls(
            board_id=data["board_id"],
            scraped_count=data.get("scraped_count", len(data.get("data", {}))),
            data=data.get("data", {}),
            scraped_at=data.get("scraped_at")
        )
    
    def is_empty(self) -> bool:
        """스크래핑된 데이터가 비어있는지 확인"""
        return self.scraped_count == 0
    
    def get_post_ids(self) -> list:
        """스크래핑된 게시물 ID 목록 반환"""
        return list(self.data.keys())
    
    def get_post_by_id(self, post_id: str) -> ScrapedPost:
        """특정 ID의 게시물 반환"""
        return self.data.get(post_id)
    
    def __len__(self) -> int:
        """len() 함수 지원"""
        return self.scraped_count
    
    def __iter__(self):
        """for문 지원 - 게시물 데이터 순회"""
        return iter(self.data.items())
    
    def __repr__(self) -> str:
        return f"ScrapedPostsDto(board_id={self.board_id}, scraped_count={self.scraped_count}, scraped_at={self.scraped_at})"