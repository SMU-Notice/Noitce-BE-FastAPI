import os
from pydantic import BaseModel
from typing import Dict, Literal

class ScraperConfig(BaseModel):
    board_id: int
    base_url: str
    params: Dict[str, str | int]
    interval: int
    campus: Literal["sang", "seoul"]

# 스크래퍼 이름 기반 board_id
MAIN_BOARD_SANGMYUNG_BOARD_ID = int(os.getenv("MAIN_BOARD_SANGMYUNG_BOARD_ID"))
MAIN_BOARD_SEOUL_BOARD_ID = int(os.getenv("MAIN_BOARD_SEOUL_BOARD_ID"))

LIB_NOTICE_BOARD_ID          = int(os.getenv("LIB_NOTICE_BOARD_ID"))
LIB_EDUBOARD_BOARD_ID        = int(os.getenv("LIB_EDUBOARD_BOARD_ID"))

CS_NOTICE_BOARD_ID           = int(os.getenv("CS_NOTICE_BOARD_ID"))
CS_SUGANG_BOARD_ID           = int(os.getenv("CS_SUGANG_BOARD_ID"))
SLS_NOTICE_BOARD_ID          = int(os.getenv("SLS_NOTICE_BOARD_ID"))
HISTORY_NOTICE_BOARD_ID      = int(os.getenv("HISTORY_NOTICE_BOARD_ID"))
CC_NOTICE_BOARD_ID           = int(os.getenv("CC_NOTICE_BOARD_ID"))
LIBINFO_NOTICE_BOARD_ID      = int(os.getenv("LIBINFO_NOTICE_BOARD_ID"))
KJC_NOTICE_BOARD_ID          = int(os.getenv("KJC_NOTICE_BOARD_ID"))
SPACE_NOTICE_BOARD_ID        = int(os.getenv("SPACE_NOTICE_BOARD_ID"))
PUBLIC_NOTICE_BOARD_ID       = int(os.getenv("PUBLIC_NOTICE_BOARD_ID"))
SMFAMILY_NOTICE_BOARD_ID     = int(os.getenv("SMFAMILY_NOTICE_BOARD_ID"))
NS_NOTICE_BOARD_ID           = int(os.getenv("NS_NOTICE_BOARD_ID"))
KOREDU_NOTICE_BOARD_ID       = int(os.getenv("KOREDU_NOTICE_BOARD_ID"))
ENGEDU_NOTICE_BOARD_ID       = int(os.getenv("ENGEDU_NOTICE_BOARD_ID"))
LEARNING_NOTICE_BOARD_ID     = int(os.getenv("LEARNING_NOTICE_BOARD_ID"))
MATHED_NOTICE_BOARD_ID       = int(os.getenv("MATHED_NOTICE_BOARD_ID"))
SMUBIZ_NOTICE_BOARD_ID       = int(os.getenv("SMUBIZ_NOTICE_BOARD_ID"))
SBE_NOTICE_BOARD_ID          = int(os.getenv("SBE_NOTICE_BOARD_ID"))
GBIZ_NOTICE_BOARD_ID         = int(os.getenv("GBIZ_NOTICE_BOARD_ID"))
CM_NOTICE_BOARD_ID           = int(os.getenv("CM_NOTICE_BOARD_ID"))
ELECTRIC_NOTICE_BOARD_ID     = int(os.getenv("ELECTRIC_NOTICE_BOARD_ID"))
AIOT_NOTICE_BOARD_ID         = int(os.getenv("AIOT_NOTICE_BOARD_ID"))
GAME_NOTICE_BOARD_ID         = int(os.getenv("GAME_NOTICE_BOARD_ID"))
ANIMATION_NOTICE_BOARD_ID    = int(os.getenv("ANIMATION_NOTICE_BOARD_ID"))
HI_NOTICE_BOARD_ID           = int(os.getenv("HI_NOTICE_BOARD_ID"))
FBS_NOTICE_BOARD_ID          = int(os.getenv("FBS_NOTICE_BOARD_ID"))
BIO_NOTICE_BOARD_ID          = int(os.getenv("BIO_NOTICE_BOARD_ID"))
ICHEM_NOTICE_BOARD_ID        = int(os.getenv("ICHEM_NOTICE_BOARD_ID"))
ENERGY_NOTICE_BOARD_ID       = int(os.getenv("ENERGY_NOTICE_BOARD_ID"))
FOOD_NOTICE_BOARD_ID         = int(os.getenv("FOOD_NOTICE_BOARD_ID"))
FASHION_NOTICE_BOARD_ID      = int(os.getenv("FASHION_NOTICE_BOARD_ID"))
SPORTS_NOTICE_BOARD_ID       = int(os.getenv("SPORTS_NOTICE_BOARD_ID"))
DANCE_NOTICE_BOARD_ID        = int(os.getenv("DANCE_NOTICE_BOARD_ID"))
FINEARTS_NOTICE_BOARD_ID     = int(os.getenv("FINEARTS_NOTICE_BOARD_ID"))
SMULAD_NOTICE_BOARD_ID       = int(os.getenv("SMULAD_NOTICE_BOARD_ID"))
MUSIC_NOTICE_BOARD_ID        = int(os.getenv("MUSIC_NOTICE_BOARD_ID"))

HAPPYDORM_NOTICE_BOARD_ID    = int(os.getenv("HAPPYDORM_NOTICE_BOARD_ID"))
SMUDORM_NOTICE_BOARD_ID      = int(os.getenv("SMUDORM_NOTICE_BOARD_ID"))
FOREIGN_NOTICE_BOARD_ID      = int(os.getenv("FOREIGN_NOTICE_BOARD_ID"))
GRAD_NOTICE_BOARD_ID         = int(os.getenv("GRAD_NOTICE_BOARD_ID"))
ICEE_NOTICE_BOARD_ID         = int(os.getenv("ICEE_NOTICE_BOARD_ID"))
SWAI_NOTICE_BOARD_ID         = int(os.getenv("SWAI_NOTICE_BOARD_ID"))


# 스크래퍼 이름 기반 interval 환경변수 (기본값: 3600초 = 1시간)
MAIN_BOARD_SANGMYUNG_INTERVAL = int(os.getenv("MAIN_BOARD_SANGMYUNG_INTERVAL", 3600))
MAIN_BOARD_SEOUL_INTERVAL = int(os.getenv("MAIN_BOARD_SEOUL_INTERVAL", 3600))


LIB_NOTICE_INTERVAL            = int(os.getenv("LIB_NOTICE_INTERVAL", 3600))
LIB_EDUBOARD_INTERVAL          = int(os.getenv("LIB_EDUBOARD_INTERVAL", 3600))



CS_NOTICE_INTERVAL = int(os.getenv("CS_NOTICE_INTERVAL", 3600))
CS_SUGANG_INTERVAL = int(os.getenv("CS_SUGANG_INTERVAL", 3600))
SLS_NOTICE_INTERVAL = int(os.getenv("SLS_NOTICE_INTERVAL", 3600))
HISTORY_NOTICE_INTERVAL = int(os.getenv("HISTORY_NOTICE_INTERVAL", 3600))
CC_NOTICE_INTERVAL = int(os.getenv("CC_NOTICE_INTERVAL", 3600))
LIBINFO_NOTICE_INTERVAL = int(os.getenv("LIBINFO_NOTICE_INTERVAL", 3600))
KJC_NOTICE_INTERVAL = int(os.getenv("KJC_NOTICE_INTERVAL", 3600))
SPACE_NOTICE_INTERVAL = int(os.getenv("SPACE_NOTICE_INTERVAL", 3600))
PUBLIC_NOTICE_INTERVAL = int(os.getenv("PUBLIC_NOTICE_INTERVAL", 3600))
SMFAMILY_NOTICE_INTERVAL = int(os.getenv("SMFAMILY_NOTICE_INTERVAL", 3600))
NS_NOTICE_INTERVAL = int(os.getenv("NS_NOTICE_INTERVAL", 3600))
KOREDU_NOTICE_INTERVAL       = int(os.getenv("KOREDU_NOTICE_INTERVAL", 3600))
ENGEDU_NOTICE_INTERVAL       = int(os.getenv("ENGEDU_NOTICE_INTERVAL", 3600))
LEARNING_NOTICE_INTERVAL     = int(os.getenv("LEARNING_NOTICE_INTERVAL", 3600))
MATHED_NOTICE_INTERVAL       = int(os.getenv("MATHED_NOTICE_INTERVAL", 3600))
SMUBIZ_NOTICE_INTERVAL       = int(os.getenv("SMUBIZ_NOTICE_INTERVAL", 3600))
SBE_NOTICE_INTERVAL          = int(os.getenv("SBE_NOTICE_INTERVAL", 3600))
GBIZ_NOTICE_INTERVAL         = int(os.getenv("GBIZ_NOTICE_INTERVAL", 3600))
CM_NOTICE_INTERVAL           = int(os.getenv("CM_NOTICE_INTERVAL", 3600))
ELECTRIC_NOTICE_INTERVAL     = int(os.getenv("ELECTRIC_NOTICE_INTERVAL", 3600))
AIOT_NOTICE_INTERVAL         = int(os.getenv("AIOT_NOTICE_INTERVAL", 3600))
GAME_NOTICE_INTERVAL         = int(os.getenv("GAME_NOTICE_INTERVAL", 3600))
ANIMATION_NOTICE_INTERVAL    = int(os.getenv("ANIMATION_NOTICE_INTERVAL", 3600))
HI_NOTICE_INTERVAL           = int(os.getenv("HI_NOTICE_INTERVAL", 3600))
FBS_NOTICE_INTERVAL          = int(os.getenv("FBS_NOTICE_INTERVAL", 3600))
BIO_NOTICE_INTERVAL          = int(os.getenv("BIO_NOTICE_INTERVAL", 3600))
ICHEM_NOTICE_INTERVAL        = int(os.getenv("ICHEM_NOTICE_INTERVAL", 3600))
ENERGY_NOTICE_INTERVAL       = int(os.getenv("ENERGY_NOTICE_INTERVAL", 3600))
FOOD_NOTICE_INTERVAL         = int(os.getenv("FOOD_NOTICE_INTERVAL", 3600))
FASHION_NOTICE_INTERVAL      = int(os.getenv("FASHION_NOTICE_INTERVAL", 3600))
SPORTS_NOTICE_INTERVAL       = int(os.getenv("SPORTS_NOTICE_INTERVAL", 3600))
DANCE_NOTICE_INTERVAL        = int(os.getenv("DANCE_NOTICE_INTERVAL", 3600))
FINEARTS_NOTICE_INTERVAL     = int(os.getenv("FINEARTS_NOTICE_INTERVAL", 3600))
SMULAD_NOTICE_INTERVAL       = int(os.getenv("SMULAD_NOTICE_INTERVAL", 3600))
MUSIC_NOTICE_INTERVAL        = int(os.getenv("MUSIC_NOTICE_INTERVAL", 3600))

HAPPYDORM_NOTICE_INTERVAL        = int(os.getenv("HAPPYDORM_NOTICE_INTERVAL", 3600))
SMUDORM_NOTICE_INTERVAL        = int(os.getenv("SMUDORM_NOTICE_INTERVAL", 3600))
FOREIGN_NOTICE_INTERVAL        = int(os.getenv("FOREIGN_NOTICE_INTERVAL", 3600))
GRAD_NOTICE_INTERVAL        = int(os.getenv("GRAD_NOTICE_INTERVAL", 3600))
ICEE_NOTICE_INTERVAL        = int(os.getenv("ICEE_NOTICE_INTERVAL", 3600))
SWAI_NOTICE_INTERVAL        = int(os.getenv("SWAI_NOTICE_INTERVAL", 3600))

SCRAPER_CONFIGS = {
    "main_board_sangmyung": ScraperConfig(
        board_id=MAIN_BOARD_SANGMYUNG_BOARD_ID,
        base_url="https://www.smu.ac.kr/kor/life/notice.do",
        params={
            "srCampus": "smu",
            "mode": "list",
            "articleLimit": 50,
            "article.offset": 0
        },
        interval=MAIN_BOARD_SANGMYUNG_INTERVAL,
        campus="sang"
    ),
    "main_board_seoul": ScraperConfig(
        board_id=MAIN_BOARD_SEOUL_BOARD_ID,
        base_url="https://www.smu.ac.kr/kor/life/notice.do",
        params={
            "srCampus": "smu",
            "mode": "list",
            "articleLimit": 50,
            "article.offset": 0
        },
        interval=MAIN_BOARD_SEOUL_INTERVAL,
        campus="seoul"
    ),
    # 학술정보관 공지사항
    "lib_notice": ScraperConfig(
        board_id=LIB_NOTICE_BOARD_ID,
        base_url="https://lib.smu.ac.kr/Board?n=notice",
        params={
            "p": 1    # 1페이지 대상으로 스크래핑
        },
        interval=LIB_NOTICE_INTERVAL,
        campus="seoul"    
    ),

    # 학술정보관 교육공지
    "lib_eduboard": ScraperConfig(
        board_id=LIB_EDUBOARD_BOARD_ID,
        base_url="https://lib.smu.ac.kr/Board?n=eduboard",
        params={
            "p": 1
        },
        interval=LIB_EDUBOARD_INTERVAL,
        campus="seoul"
    ),

    # 컴퓨터과학전공 공지사항
    "cs_notice": ScraperConfig(
        board_id=CS_NOTICE_BOARD_ID,  
        base_url="https://cs.smu.ac.kr/cs/community/notice.do",
        params={
            "mode": "list",          
            "articleLimit": 50,      
            "article.offset": 0      
        },
        interval=CS_NOTICE_INTERVAL,
        campus="seoul"
    ),

    # 컴퓨터과학전공 수강신청
    "cs_sugang": ScraperConfig(
        board_id=CS_SUGANG_BOARD_ID,
        base_url="https://cs.smu.ac.kr/cs/admission/sugang.do",
        params={
            "mode": "list",
            "articleLimit": 50,
            "article.offset": 0
        },
        interval=CS_SUGANG_INTERVAL,
        campus="seoul"
    ),
    # 자유전공학부대학 게시판
    "sls_notice": ScraperConfig(
        board_id=SLS_NOTICE_BOARD_ID,  
        base_url="https://www.smu.ac.kr/sls/community/notice.do",
        params={
            "mode": "list",          
            "articleLimit": 50,      
            "article.offset": 0      
        },
        interval=SLS_NOTICE_INTERVAL,
        campus="seoul"
    ),

# 역사콘텐츠전공 게시판
    "history_notice": ScraperConfig(
        board_id=HISTORY_NOTICE_BOARD_ID,  
        base_url="https://history.smu.ac.kr/history/community/notice.do",
        params={
            "mode": "list",          
            "articleLimit": 50,      
            "article.offset": 0      
        },
        interval=HISTORY_NOTICE_INTERVAL,
        campus="seoul"
    ),

# 지적재산권전공 게시판
    "cc_notice": ScraperConfig(
        board_id=CC_NOTICE_BOARD_ID,  
        base_url="https://cr.smu.ac.kr/cc/community/notice.do",
        params={
            "mode": "list",          
            "articleLimit": 50,      
            "article.offset": 0      
        },
        interval=CC_NOTICE_INTERVAL,
        campus="seoul"
    ),

# 문헌정보학전공 게시판
    "libinfo_notice": ScraperConfig(
        board_id=LIBINFO_NOTICE_BOARD_ID,  
        base_url="https://libinfo.smu.ac.kr/libinfo/community/notice.do",
        params={
            "mode": "list",          
            "articleLimit": 50,      
            "article.offset": 0      
        },
        interval=LIBINFO_NOTICE_INTERVAL,
        campus="seoul"
    ),

# 한일문화콘텐츠전공 게시판
    "kjc_notice": ScraperConfig(
        board_id=KJC_NOTICE_BOARD_ID,  
        base_url="https://kjc.smu.ac.kr/kjc/community/notice.do",
        params={
            "mode": "list",          
            "articleLimit": 50,      
            "article.offset": 0      
        },
        interval=KJC_NOTICE_INTERVAL,
        campus="seoul"
    ),

# 공간환경학부 게시판
    "space_notice": ScraperConfig(
        board_id=SPACE_NOTICE_BOARD_ID,  
        base_url="https://space.smu.ac.kr/space/community/notice.do",
        params={
            "mode": "list",          
            "articleLimit": 50,      
            "article.offset": 0      
        },
        interval=SPACE_NOTICE_INTERVAL,
        campus="seoul"
    ),

# 행정학부 게시판
    "public_notice": ScraperConfig(
        board_id=PUBLIC_NOTICE_BOARD_ID,  
        base_url="https://public.smu.ac.kr/public/community/notice.do#noMenu",
        params={
            "mode": "list",          
            "articleLimit": 50,      
            "article.offset": 0      
        },
        interval=PUBLIC_NOTICE_INTERVAL,
        campus="seoul"
    ),

# 가족복지학과 게시판
    "smfamily_notice": ScraperConfig(
        board_id=SMFAMILY_NOTICE_BOARD_ID,  
        base_url="https://smfamily.smu.ac.kr/smfamily/community/notice.do",
        params={
            "mode": "list",          
            "articleLimit": 50,      
            "article.offset": 0      
        },
        interval=SMFAMILY_NOTICE_INTERVAL,
        campus="seoul"
    ),

# 국가안보학과 게시판
    "ns_notice": ScraperConfig(
        board_id=NS_NOTICE_BOARD_ID,  
        base_url="https://ns.smu.ac.kr/sdms/community/notice.do",
        params={
            "mode": "list",          
            "articleLimit": 50,      
            "article.offset": 0      
        },
        interval=NS_NOTICE_INTERVAL,
        campus="seoul"
    ),

# 국어교육과 게시판
    "koredu_notice": ScraperConfig(
        board_id=KOREDU_NOTICE_BOARD_ID,  
        base_url="https://koredu.smu.ac.kr/koredu/community/notice.do",
        params={
            "mode": "list",          
            "articleLimit": 50,      
            "article.offset": 0      
        },
        interval=KOREDU_NOTICE_INTERVAL,
        campus="seoul"
    ),

# 영어교육과 게시판
    "engedu_notice": ScraperConfig(
        board_id=ENGEDU_NOTICE_BOARD_ID,  
        base_url="https://engedu.smu.ac.kr/engedu/community/notice.do",
        params={
            "mode": "list",          
            "articleLimit": 50,      
            "article.offset": 0      
        },
        interval=ENGEDU_NOTICE_INTERVAL,
        campus="seoul"
    ),

# 교육학과 게시판
    "learning_notice": ScraperConfig(
        board_id=LEARNING_NOTICE_BOARD_ID,  
        base_url="https://learning.smu.ac.kr/peda/community/notice.do",
        params={
            "mode": "list",          
            "articleLimit": 50,      
            "article.offset": 0      
        },
        interval=LEARNING_NOTICE_INTERVAL,
        campus="seoul"
    ),

# 수학교육과 게시판
    "mathed_notice": ScraperConfig(
        board_id=MATHED_NOTICE_BOARD_ID,  
        base_url="https://mathed.smu.ac.kr/mathedu/community/notice.do",
        params={
            "mode": "list",          
            "articleLimit": 50,      
            "article.offset": 0      
        },
        interval=MATHED_NOTICE_INTERVAL,
        campus="seoul"
    ),

# 경영학부 게시판
    "smubiz_notice": ScraperConfig(
        board_id=SMUBIZ_NOTICE_BOARD_ID,  
        base_url="https://smubiz.smu.ac.kr/smubiz/community/notice.do",
        params={
            "mode": "list",          
            "articleLimit": 50,      
            "article.offset": 0      
        },
        interval=SMUBIZ_NOTICE_INTERVAL,
        campus="seoul"
    ),

# 경제금융학부 게시판
    "sbe_notice": ScraperConfig(
        board_id=SBE_NOTICE_BOARD_ID,  
        base_url="https://sbe.smu.ac.kr/economic/community/notice.do",
        params={
            "mode": "list",          
            "articleLimit": 50,      
            "article.offset": 0      
        },
        interval=SBE_NOTICE_INTERVAL,
        campus="seoul"
    ),

# 글로벌경영학과 게시판
    "gbiz_notice": ScraperConfig(
        board_id=GBIZ_NOTICE_BOARD_ID,  
        base_url="https://gbiz.smu.ac.kr/newmajoritb/board/notice.do",
        params={
            "mode": "list",          
            "articleLimit": 50,      
            "article.offset": 0      
        },
        interval=GBIZ_NOTICE_INTERVAL,
        campus="seoul"
    ),

# 융합경영학과 게시판
    "cm_notice": ScraperConfig(
        board_id=CM_NOTICE_BOARD_ID,  
        base_url="https://www.smu.ac.kr/cm/community/notice.do",
        params={
            "mode": "list",          
            "articleLimit": 50,      
            "article.offset": 0      
        },
        interval=CM_NOTICE_INTERVAL,
        campus="seoul"
    ),

# 전기공학전공 게시판
    "electric_notice": ScraperConfig(
        board_id=ELECTRIC_NOTICE_BOARD_ID,  
        base_url="https://electric.smu.ac.kr/electric/community/notice.do",
        params={
            "mode": "list",          
            "articleLimit": 50,      
            "article.offset": 0      
        },
        interval=ELECTRIC_NOTICE_INTERVAL,
        campus="seoul"
    ),

# 지능IOT융합전공 게시판
    "aiot_notice": ScraperConfig(
        board_id=AIOT_NOTICE_BOARD_ID,  
        base_url="https://aiot.smu.ac.kr/aiot/community/notice.do",
        params={
            "mode": "list",          
            "articleLimit": 50,      
            "article.offset": 0      
        },
        interval=AIOT_NOTICE_INTERVAL,
        campus="seoul"
    ),

# 게임전공 게시판
    "game_notice": ScraperConfig(
        board_id=GAME_NOTICE_BOARD_ID,  
        base_url="https://game.smu.ac.kr/game01/community/notice.do",
        params={
            "mode": "list",          
            "articleLimit": 50,      
            "article.offset": 0      
        },
        interval=GAME_NOTICE_INTERVAL,
        campus="seoul"
    ),

# 애니메이션전공 게시판
    "animation_notice": ScraperConfig(
        board_id=ANIMATION_NOTICE_BOARD_ID,  
        base_url="https://animation.smu.ac.kr/animation/community/notice.do",
        params={
            "mode": "list",          
            "articleLimit": 50,      
            "article.offset": 0      
        },
        interval=ANIMATION_NOTICE_INTERVAL,
        campus="seoul"
    ),

# 휴먼지능정보공학전공 게시판
    "hi_notice": ScraperConfig(
        board_id=HI_NOTICE_BOARD_ID,  
        base_url="https://hi.smu.ac.kr/hi/community/notice.do",
        params={
            "mode": "list",          
            "articleLimit": 50,      
            "article.offset": 0      
        },
        interval=HI_NOTICE_INTERVAL,
        campus="seoul"
    ),

# 핀테크 빅데이터융합 스마트생산전공 게시판
    "fbs_notice": ScraperConfig(
        board_id=FBS_NOTICE_BOARD_ID,  
        base_url="https://fbs.smu.ac.kr/fbs/community/notice.do",
        params={
            "mode": "list",          
            "articleLimit": 50,      
            "article.offset": 0      
        },
        interval=FBS_NOTICE_INTERVAL,
        campus="seoul"
    ),

# 생명공학전공 게시판
    "bio_notice": ScraperConfig(
        board_id=BIO_NOTICE_BOARD_ID,  
        base_url="https://biotechnology.smu.ac.kr/biotechnology/community/notice.do",
        params={
            "mode": "list",          
            "articleLimit": 50,      
            "article.offset": 0      
        },
        interval=BIO_NOTICE_INTERVAL,
        campus="seoul"
    ),

# 화공신소재전공 게시판
    "ichem_notice": ScraperConfig(
        board_id=ICHEM_NOTICE_BOARD_ID,  
        base_url="https://ichem.smu.ac.kr/ichemistry/community/notice.do",
        params={
            "mode": "list",          
            "articleLimit": 50,      
            "article.offset": 0      
        },
        interval=ICHEM_NOTICE_INTERVAL,
        campus="seoul"
    ),

# 화학에너지공학전공 게시판
    "energy_notice": ScraperConfig(
        board_id=ENERGY_NOTICE_BOARD_ID,  
        base_url="https://energy.smu.ac.kr/cee/community/notice.do",
        params={
            "mode": "list",          
            "articleLimit": 50,      
            "article.offset": 0      
        },
        interval=ENERGY_NOTICE_INTERVAL,
        campus="seoul"
    ),

# 식품영양학전공 게시판
    "food_notice": ScraperConfig(
        board_id=FOOD_NOTICE_BOARD_ID,  
        base_url="https://www.smu.ac.kr/foodnutrition/community/notice.do",
        params={
            "mode": "list",          
            "articleLimit": 50,      
            "article.offset": 0      
        },
        interval=FOOD_NOTICE_INTERVAL,
        campus="seoul"
    ),

# 의류학전공 게시판
    "fashion_notice": ScraperConfig(
        board_id=FASHION_NOTICE_BOARD_ID,  
        base_url="https://fashionindustry.smu.ac.kr/clothing2/community/notice.do",
        params={
            "mode": "list",          
            "articleLimit": 50,      
            "article.offset": 0      
        },
        interval=FASHION_NOTICE_INTERVAL,
        campus="seoul"
    ),

# 스포츠건강관리전공 게시판
    "sports_notice": ScraperConfig(
        board_id=SPORTS_NOTICE_BOARD_ID,  
        base_url="https://sports.smu.ac.kr/smpe/community/notice.do",
        params={
            "mode": "list",          
            "articleLimit": 50,      
            "article.offset": 0      
        },
        interval=SPORTS_NOTICE_INTERVAL,
        campus="seoul"
    ),

# 무용예술전공 게시판
    "dance_notice": ScraperConfig(
        board_id=DANCE_NOTICE_BOARD_ID,  
        base_url="https://dance.smu.ac.kr/dance/undergraduate/undergraduate_notice.do",
        params={
            "mode": "list",          
            "articleLimit": 50,      
            "article.offset": 0      
        },
        interval=DANCE_NOTICE_INTERVAL,
        campus="seoul"
    ),

# 조형예술전공 게시판
    "finearts_notice": ScraperConfig(
        board_id=FINEARTS_NOTICE_BOARD_ID,  
        base_url="https://finearts.smu.ac.kr/finearts/community/notice1.do",
        params={
            "mode": "list",          
            "articleLimit": 50,      
            "article.offset": 0      
        },
        interval=FINEARTS_NOTICE_INTERVAL,
        campus="seoul"
    ),

# 생활예술전공 게시판
    "smulad_notice": ScraperConfig(
        board_id=SMULAD_NOTICE_BOARD_ID,  
        base_url="https://smulad.smu.ac.kr/smulad/community/notice.do",
        params={
            "mode": "list",          
            "articleLimit": 50,      
            "article.offset": 0      
        },
        interval=SMULAD_NOTICE_INTERVAL,
        campus="seoul"
    ),

# 음악학부 게시판
    "music_notice": ScraperConfig(
        board_id=MUSIC_NOTICE_BOARD_ID,  
        base_url="https://music.smu.ac.kr/music/community/notice.do",
        params={
            "mode": "list",          
            "articleLimit": 50,      
            "article.offset": 0      
        },
        interval=MUSIC_NOTICE_INTERVAL,
        campus="seoul"
    ),
# 상명행복생활관 게시판
    "happydorm_notice": ScraperConfig(
        board_id=HAPPYDORM_NOTICE_BOARD_ID,  
        base_url="https://dormitory.smu.ac.kr/dormi/happy/happy_notice.do",
        params={
            "mode": "list",          
            "articleLimit": 50,      
            "article.offset": 0      
        },
        interval=HAPPYDORM_NOTICE_INTERVAL,
        campus="seoul"
    ),
# 스뮤하우스 게시판
    "smudorm_notice": ScraperConfig(
        board_id=SMUDORM_NOTICE_BOARD_ID,  
        base_url="https://dormitory.smu.ac.kr/dormi/smu/smu_notice.do",
        params={
            "mode": "list",          
            "articleLimit": 50,      
            "article.offset": 0      
        },
        interval=SMUDORM_NOTICE_INTERVAL,
        campus="seoul"
    ),    
# 대외협력처 게시판
    "foreign_notice": ScraperConfig(
        board_id=FOREIGN_NOTICE_BOARD_ID,  
        base_url="https://www.smu.ac.kr/oia/foreign/notice02.do",
        params={
            "mode": "list",          
            "articleLimit": 50,      
            "article.offset": 0      
        },
        interval=FOREIGN_NOTICE_INTERVAL,
        campus="seoul"
    ),  
# 일반대학원 게시판
    "grad_notice": ScraperConfig(
        board_id=GRAD_NOTICE_BOARD_ID,  
        base_url="https://www.smu.ac.kr/grad/board/total_notice.do",
        params={
            "mode": "list",          
            "articleLimit": 50,      
            "article.offset": 0      
        },
        interval=GRAD_NOTICE_INTERVAL,
        campus="seoul"
    ),   
# 공학교육혁신센터 게시판
    "icee_notice": ScraperConfig(
        board_id=ICEE_NOTICE_BOARD_ID,  
        base_url="https://icee.smu.ac.kr/icee/community/notice.do",
        params={
            "mode": "list",          
            "articleLimit": 50,      
            "article.offset": 0      
        },
        interval=ICEE_NOTICE_INTERVAL,
        campus="seoul"
    ),
# SW중심대학사업단 게시판
    "swai_notice": ScraperConfig(
        board_id=SWAI_NOTICE_BOARD_ID,  
        base_url="https://swai.smu.ac.kr/bbs/board.php",
        params={
            "bo_table": "07_01",     
        },
        interval=SWAI_NOTICE_INTERVAL,
        campus="seoul"
    ),

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
