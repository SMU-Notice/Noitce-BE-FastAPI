import os
from pydantic import BaseModel
from typing import Dict, Literal

class ScraperConfig(BaseModel):
    board_id: int
    base_url: str
    params: Dict[str, str | int]
    interval: int
    campus: Literal["sangmyung", "seoul"]

# 스크래퍼 이름 기반 interval 환경변수 (기본값: 3600초 = 1시간)
MAIN_BOARD_SANGMYUNG_INTERVAL = int(os.getenv("MAIN_BOARD_SANGMYUNG_INTERVAL", 3600))
MAIN_BOARD_SEOUL_INTERVAL = int(os.getenv("MAIN_BOARD_SEOUL_INTERVAL", 3600))

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
        interval=MAIN_BOARD_SANGMYUNG_INTERVAL,
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
        interval=MAIN_BOARD_SEOUL_INTERVAL,
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