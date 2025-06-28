from pydantic import BaseModel
from typing import Dict, Literal

class ScraperConfig(BaseModel):
    board_id: int
    base_url: str
    params: Dict[str, str | int]
    interval: int
    campus: Literal["sangmyung", "seoul"]

SCRAPER_CONFIGS = {
    "main_board_sangmyung": ScraperConfig(
        board_id=1,
        base_url="https://www.smu.ac.kr/kor/life/notice.do",
        params={
            "srCampus": "smu",
            "mode": "list",
            "articleLimit": 50,
            "article.offset": 0
        },
        interval=10,  # 1시간
        campus="sangmyung"
    ),
    "main_board_seoul": ScraperConfig(
        board_id=2,
        base_url="https://www.smu.ac.kr/kor/life/notice.do",
        params={
            "srCampus": "smu",
            "mode": "list",
            "articleLimit": 50,
            "article.offset": 0
        },
        interval=10,  # 1시간
        campus="seoul"
    )
}

def get_scraper_config(scraper_name: str) -> ScraperConfig:
    """
    스크래퍼 이름에 해당하는 설정을 반환합니다.
    
    Args:
        scraper_name (str): 스크래퍼 이름
        
    Returns:
        ScraperConfig: 스크래퍼 설정
    """
    return SCRAPER_CONFIGS.get(scraper_name)
