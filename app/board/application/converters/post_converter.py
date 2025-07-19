from datetime import datetime
from typing import Dict, Any, List
from app.board.domain.post import Post
from app.board.infra.scraper.models.scraped_post import ScrapedPost


class PostConverter:
    """스크래핑 데이터를 도메인 객체로 변환하는 클래스"""
    
    @staticmethod
    def scraped_to_domain(scraped: ScrapedPost, board_id: int) -> Post:
        """
        ScrapedPost를 Post 도메인 객체로 변환
        
        Parameters:
        - scraped: 스크래핑된 게시물 데이터
        - board_id: 게시판 ID
        
        Returns:
        - Post: 도메인 객체
        """
        return Post(
            board_id=board_id,
            original_post_id=int(scraped.original_post_id),
            post_type=scraped.post_type,
            title=scraped.title,
            url=scraped.url,
            posted_date=datetime.strptime(scraped.date, "%Y-%m-%d").date(),
            view_count=int(scraped.view_count),
            has_reference=scraped.has_reference
        )
    
    @staticmethod
    def convert_scraped_data_to_domain(scraped_posts_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        스크래핑된 딕셔너리 데이터를 도메인 객체로 변환
        
        Parameters:
        - scraped_posts_dict: {"board_id": int, "scraped_count": int, "data": {...}}
        
        Returns:
        - Dict: data 부분이 Post 객체로 변환된 딕셔너리
        """
        board_id = scraped_posts_dict["board_id"]
        scraped_data = scraped_posts_dict["data"]
        
        # data를 도메인 객체로 변환
        converted_data = {
            original_post_id: PostConverter.scraped_to_domain(scraped_post, board_id)
            for original_post_id, scraped_post in scraped_data.items()
        }
        
        # 원본 구조 유지하면서 data만 교체
        result = scraped_posts_dict.copy()
        result["data"] = converted_data
        
        return result
    
    @staticmethod
    def convert_scraped_data_to_post_list(scraped_posts_dict: Dict[str, Any]) -> List[Post]:
        """
        스크래핑된 딕셔너리 데이터를 Post 도메인 객체 리스트로 변환
        
        Parameters:
        - scraped_posts_dict: {"board_id": int, "scraped_count": int, "data": {...}}
        
        Returns:
        - List[Post]: Post 도메인 객체 리스트
        """
        board_id = scraped_posts_dict["board_id"]
        scraped_data = scraped_posts_dict["data"]
        
        # data를 Post 객체 리스트로 변환
        post_list = [
            PostConverter.scraped_to_domain(scraped_post, board_id)
            for original_post_id, scraped_post in scraped_data.items()
        ]
        
        return post_list