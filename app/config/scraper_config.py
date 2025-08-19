import os
from pydantic import BaseModel
from typing import Dict, Literal

class ScraperConfig(BaseModel):
   board_id: int
   base_url: str
   params: Dict[str, str | int]
   interval: int
   campus: Literal["sangmyung", "seoul"]

class EnvVars:
   def __getattr__(self, name):
       value = os.getenv(name)
       if value is None:
           raise AttributeError(f"Environment variable {name} not found")
       try:
           return int(value)
       except ValueError:
           return value

env = EnvVars()

SCRAPER_CONFIGS = {
   "main_board_sangmyung": ScraperConfig(
       board_id=env.MAIN_BOARD_SANGMYUNG_BOARD_ID,
       base_url="https://www.smu.ac.kr/kor/life/notice.do",
       params={
           "srCampus": "smu",
           "mode": "list",
           "articleLimit": 50,
           "article.offset": 0
       },
       interval=env.MAIN_BOARD_SANGMYUNG_INTERVAL,
       campus="sangmyung"
   ),
   "main_board_seoul": ScraperConfig(
       board_id=env.MAIN_BOARD_SEOUL_BOARD_ID,
       base_url="https://www.smu.ac.kr/kor/life/notice.do",
       params={
           "srCampus": "smu",
           "mode": "list",
           "articleLimit": 50,
           "article.offset": 0
       },
       interval= env.MAIN_BOARD_SEOUL_INTERVAL,
       campus="seoul"
   ),
   "lib_notice": ScraperConfig(
       board_id=env.LIB_NOTICE_BOARD_ID,
       base_url="https://lib.smu.ac.kr/Board?n=notice",
        params={
            "p": 1    # 1페이지
        },
       interval= env.LIB_NOTICE_INTERVAL,
       campus="seoul"
   ),
   "lib_eduboard": ScraperConfig(
       board_id=env.LIB_EDUBOARD_BOARD_ID,
       base_url="https://lib.smu.ac.kr/Board?n=eduboard",
        params={
            "p": 1    # 1페이지
        },
       interval= env.LIB_EDUBOARD_INTERVAL,
       campus="seoul"
   ),
   "cs_notice": ScraperConfig(
       board_id=env.CS_NOTICE_BOARD_ID,
       base_url="https://cs.smu.ac.kr/cs/community/notice.do",
       params={
           "mode": "list",
           "articleLimit": 50,
           "article.offset": 0
       },
       interval= env.CS_NOTICE_INTERVAL,
       campus="seoul"
   ),
   "cs_sugang": ScraperConfig(
       board_id=env.CS_SUGANG_BOARD_ID,
       base_url="https://cs.smu.ac.kr/cs/admission/sugang.do",
       params={
           "mode": "list",
           "articleLimit": 50,
           "article.offset": 0
       },
       interval= env.CS_SUGANG_INTERVAL,
       campus="seoul"
   ),      
   "sls_notice": ScraperConfig(
       board_id=env.SLS_NOTICE_BOARD_ID,
       base_url="https://www.smu.ac.kr/sls/community/notice.do",
       params={
           "mode": "list",
           "articleLimit": 50,
           "article.offset": 0
       },
       interval= env.SLS_NOTICE_INTERVAL,
       campus="seoul"
   ),
   "history_notice": ScraperConfig(
       board_id=env.HISTORY_NOTICE_BOARD_ID,
       base_url="https://history.smu.ac.kr/history/community/notice.do",
       params={
           "mode": "list",
           "articleLimit": 50,
           "article.offset": 0
       },
       interval= env.HISTORY_NOTICE_INTERVAL,
       campus="seoul"
   ),
   "cc_notice": ScraperConfig(
       board_id=env.CC_NOTICE_BOARD_ID,
       base_url="https://cr.smu.ac.kr/cc/community/notice.do",
       params={
           "mode": "list",
           "articleLimit": 50,
           "article.offset": 0
       },
       interval= env.CC_NOTICE_INTERVAL,
       campus="seoul"
   ),
   "libinfo_notice": ScraperConfig(
       board_id=env.LIBINFO_NOTICE_BOARD_ID,
       base_url="https://libinfo.smu.ac.kr/libinfo/community/notice.do",
       params={
           "mode": "list",
           "articleLimit": 50,
           "article.offset": 0
       },
       interval= env.LIBINFO_NOTICE_INTERVAL,
       campus="seoul"
   ),
   "kjc_notice": ScraperConfig(
       board_id=env.KJC_NOTICE_BOARD_ID,
       base_url="https://kjc.smu.ac.kr/kjc/community/notice.do",
       params={
           "mode": "list",
           "articleLimit": 50,
           "article.offset": 0
       },
       interval= env.KJC_NOTICE_INTERVAL,
       campus="seoul"
   ),
   "space_notice": ScraperConfig(
       board_id=env.SPACE_NOTICE_BOARD_ID,
       base_url="https://space.smu.ac.kr/space/community/notice.do",
       params={
           "mode": "list",
           "articleLimit": 50,
           "article.offset": 0
       },
       interval= env.SPACE_NOTICE_INTERVAL,
       campus="seoul"
   ),
   "public_notice": ScraperConfig(
       board_id=env.PUBLIC_NOTICE_BOARD_ID,
       base_url="https://public.smu.ac.kr/public/community/notice.do#noMenu",
       params={
           "mode": "list",
           "articleLimit": 50,
           "article.offset": 0
       },
       interval= env.PUBLIC_NOTICE_INTERVAL,
       campus="seoul"
   ),
   "smfamily_notice": ScraperConfig(
       board_id=env.SMFAMILY_NOTICE_BOARD_ID,
       base_url="https://smfamily.smu.ac.kr/smfamily/community/notice.do",
       params={
           "mode": "list",
           "articleLimit": 50,
           "article.offset": 0
       },
       interval= env.SMFAMILY_NOTICE_INTERVAL,
       campus="seoul"
   ),   
   "ns_notice": ScraperConfig(
       board_id=env.NS_NOTICE_BOARD_ID,
       base_url="https://ns.smu.ac.kr/sdms/community/notice.do",
       params={
           "mode": "list",
           "articleLimit": 50,
           "article.offset": 0
       },
       interval= env.NS_NOTICE_INTERVAL,
       campus="seoul"
   ),
   "koredu_notice": ScraperConfig(
       board_id=env.KOREDU_NOTICE_BOARD_ID,
       base_url="https://koredu.smu.ac.kr/koredu/community/notice.do",
       params={
           "mode": "list",
           "articleLimit": 50,
           "article.offset": 0
       },
       interval= env.KOREDU_NOTICE_INTERVAL,
       campus="seoul"
   ),
   "engedu_notice": ScraperConfig(
       board_id=env.ENGEDU_NOTICE_BOARD_ID,
       base_url="https://engedu.smu.ac.kr/engedu/community/notice.do",
       params={
           "mode": "list",
           "articleLimit": 50,
           "article.offset": 0
       },
       interval= env.ENGEDU_NOTICE_INTERVAL,
       campus="seoul"
   ),
   "learning_notice": ScraperConfig(
       board_id=env.LEARNING_NOTICE_BOARD_ID,
       base_url="https://learning.smu.ac.kr/peda/community/notice.do",
       params={
           "mode": "list",
           "articleLimit": 50,
           "article.offset": 0
       },
       interval= env.LEARNING_NOTICE_INTERVAL,
       campus="seoul"
   ),
   "mathed_notice": ScraperConfig(
       board_id=env.MATHED_NOTICE_BOARD_ID,
       base_url="https://mathed.smu.ac.kr/mathedu/community/notice.do",
       params={
           "mode": "list",
           "articleLimit": 50,
           "article.offset": 0
       },
       interval= env.MATHED_NOTICE_INTERVAL,
       campus="seoul"
   ),
   "smubiz_notice": ScraperConfig(
       board_id=env.SMUBIZ_NOTICE_BOARD_ID,
       base_url="https://smubiz.smu.ac.kr/smubiz/community/notice.do",
       params={
           "mode": "list",
           "articleLimit": 50,
           "article.offset": 0
       },
       interval= env.SMUBIZ_NOTICE_INTERVAL,
       campus="seoul"
   ),
   "sbe_notice": ScraperConfig(
       board_id=env.SBE_NOTICE_BOARD_ID,
       base_url="https://sbe.smu.ac.kr/economic/community/notice.do",
       params={
           "mode": "list",
           "articleLimit": 50,
           "article.offset": 0
       },
       interval= env.SBE_NOTICE_INTERVAL,
       campus="seoul"
   ),
   "gbiz_notice": ScraperConfig(
       board_id=env.GBIZ_NOTICE_BOARD_ID,
       base_url="https://gbiz.smu.ac.kr/newmajoritb/board/notice.do",
       params={
           "mode": "list",
           "articleLimit": 50,
           "article.offset": 0
       },
       interval= env.GBIZ_NOTICE_INTERVAL,
       campus="seoul"
   ),
   "cm_notice": ScraperConfig(
       board_id=env.CM_NOTICE_BOARD_ID,
       base_url="https://www.smu.ac.kr/cm/community/notice.do",
       params={
           "mode": "list",
           "articleLimit": 50,
           "article.offset": 0
       },
       interval= env.CM_NOTICE_INTERVAL,
       campus="seoul"
   ), 
   "electric_notice": ScraperConfig(
       board_id=env.ELECTRIC_NOTICE_BOARD_ID,
       base_url="https://electric.smu.ac.kr/electric/community/notice.do",
       params={
           "mode": "list",
           "articleLimit": 50,
           "article.offset": 0
       },
       interval= env.ELECTRIC_NOTICE_INTERVAL,
       campus="seoul"
   ),
   "aiot_notice": ScraperConfig(
       board_id=env.AIOT_NOTICE_BOARD_ID,
       base_url="https://aiot.smu.ac.kr/aiot/community/notice.do",
       params={
           "mode": "list",
           "articleLimit": 50,
           "article.offset": 0
       },
       interval= env.AIOT_NOTICE_INTERVAL,
       campus="seoul"
   ),
   "game_notice": ScraperConfig(
       board_id=env.GAME_NOTICE_BOARD_ID,
       base_url="https://game.smu.ac.kr/game01/community/notice.do",
       params={
           "mode": "list",
           "articleLimit": 50,
           "article.offset": 0
       },
       interval= env.GAME_NOTICE_INTERVAL,
       campus="seoul"
   ),
   "animation_notice": ScraperConfig(
       board_id=env.ANIMATION_NOTICE_BOARD_ID,
       base_url="https://animation.smu.ac.kr/animation/community/notice.do",
       params={
           "mode": "list",
           "articleLimit": 50,
           "article.offset": 0
       },
       interval= env.ANIMATION_NOTICE_INTERVAL,
       campus="seoul"
   ),
   "hi_notice": ScraperConfig(
       board_id=env.HI_NOTICE_BOARD_ID,
       base_url="https://hi.smu.ac.kr/hi/community/notice.do",
       params={
           "mode": "list",
           "articleLimit": 50,
           "article.offset": 0
       },
       interval= env.HI_NOTICE_INTERVAL,
       campus="seoul"
   ),
   "fbs_notice": ScraperConfig(
       board_id=env.FBS_NOTICE_BOARD_ID,
       base_url="https://fbs.smu.ac.kr/fbs/community/notice.do",
       params={
           "mode": "list",
           "articleLimit": 50,
           "article.offset": 0
       },
       interval= env.FBS_NOTICE_INTERVAL,
       campus="seoul"
   ),
   "bio_notice": ScraperConfig(
       board_id=env.BIO_NOTICE_BOARD_ID,
       base_url="https://biotechnology.smu.ac.kr/biotechnology/community/notice.do",
       params={
           "mode": "list",
           "articleLimit": 50,
           "article.offset": 0
       },
       interval= env.BIO_NOTICE_INTERVAL,
       campus="seoul"
   ),
   "ichem_notice": ScraperConfig(
       board_id=env.ICHEM_NOTICE_BOARD_ID,
       base_url="https://ichem.smu.ac.kr/ichemistry/community/notice.do",
       params={
           "mode": "list",
           "articleLimit": 50,
           "article.offset": 0
       },
       interval= env.ICHEM_NOTICE_INTERVAL,
       campus="seoul"
   ),
   "energy_notice": ScraperConfig(
       board_id=env.ENERGY_NOTICE_BOARD_ID,
       base_url="https://energy.smu.ac.kr/cee/community/notice.do",
       params={
           "mode": "list",
           "articleLimit": 50,
           "article.offset": 0
       },
       interval= env.ENERGY_NOTICE_INTERVAL,
       campus="seoul"
   ),
   "food_notice": ScraperConfig(
       board_id=env.FOOD_NOTICE_BOARD_ID,
       base_url="https://www.smu.ac.kr/foodnutrition/community/notice.do",
       params={
           "mode": "list",
           "articleLimit": 50,
           "article.offset": 0
       },
       interval= env.FOOD_NOTICE_INTERVAL,
       campus="seoul"
   ),
   "fashion_notice": ScraperConfig(
       board_id=env.FASHION_NOTICE_BOARD_ID,
       base_url="https://fashionindustry.smu.ac.kr/clothing2/community/notice.do",
       params={
           "mode": "list",
           "articleLimit": 50,
           "article.offset": 0
       },
       interval= env.FASHION_NOTICE_INTERVAL,
       campus="seoul"
   ),                     
   "sports_notice": ScraperConfig(
       board_id=env.SPORTS_NOTICE_BOARD_ID,
       base_url="https://sports.smu.ac.kr/smpe/community/notice.do",
       params={
           "mode": "list",
           "articleLimit": 50,
           "article.offset": 0
       },
       interval= env.SPORTS_NOTICE_INTERVAL,
       campus="seoul"
   ),
   "dance_notice": ScraperConfig(
       board_id=env.DANCE_NOTICE_BOARD_ID,
       base_url="https://dance.smu.ac.kr/dance/undergraduate/undergraduate_notice.do",
       params={
           "mode": "list",
           "articleLimit": 50,
           "article.offset": 0
       },
       interval= env.DANCE_NOTICE_INTERVAL,
       campus="seoul"
   ),
   "finearts_notice": ScraperConfig(
       board_id=env.FINEARTS_NOTICE_BOARD_ID,
       base_url="https://finearts.smu.ac.kr/finearts/community/notice1.do",
       params={
           "mode": "list",
           "articleLimit": 50,
           "article.offset": 0
       },
       interval= env.FINEARTS_NOTICE_INTERVAL,
       campus="seoul"
   ),
   "smulad_notice": ScraperConfig(
       board_id=env.SMULAD_NOTICE_BOARD_ID,
       base_url="https://smulad.smu.ac.kr/smulad/community/notice.do",
       params={
           "mode": "list",
           "articleLimit": 50,
           "article.offset": 0
       },
       interval= env.SMULAD_NOTICE_INTERVAL,
       campus="seoul"
   ),
   "music_notice": ScraperConfig(
       board_id=env.MUSIC_NOTICE_BOARD_ID,
       base_url="https://music.smu.ac.kr/music/community/notice.do",
       params={
           "mode": "list",
           "articleLimit": 50,
           "article.offset": 0
       },
       interval= env.MUSIC_NOTICE_INTERVAL,
       campus="seoul"
   ),
   "happydorm_notice": ScraperConfig(
       board_id=env.HAPPYDORM_NOTICE_BOARD_ID,
       base_url="https://dormitory.smu.ac.kr/dormi/happy/happy_notice.do",
       params={
           "mode": "list",
           "articleLimit": 50,
           "article.offset": 0
       },
       interval= env.HAPPYDORM_NOTICE_INTERVAL,
       campus="seoul"
   ),
   "smudorm_notice": ScraperConfig(
       board_id=env.SMUDORM_NOTICE_BOARD_ID,
       base_url="https://dormitory.smu.ac.kr/dormi/smu/smu_notice.do",
       params={
           "mode": "list",
           "articleLimit": 50,
           "article.offset": 0
       },
       interval= env.SMUDORM_NOTICE_INTERVAL,
       campus="seoul"
   ),
   "foreign_notice": ScraperConfig(
       board_id=env.FOREIGN_NOTICE_BOARD_ID,
       base_url="https://www.smu.ac.kr/oia/foreign/notice02.do",
       params={
           "mode": "list",
           "articleLimit": 50,
           "article.offset": 0
       },
       interval= env.FOREIGN_NOTICE_INTERVAL,
       campus="seoul"
   ),
   "grad_notice": ScraperConfig(
       board_id=env.GRAD_NOTICE_BOARD_ID,
       base_url="https://www.smu.ac.kr/grad/board/total_notice.do",
       params={
           "mode": "list",
           "articleLimit": 50,
           "article.offset": 0
       },
       interval= env.GRAD_NOTICE_INTERVAL,
       campus="seoul"
   ),
   "icee_notice": ScraperConfig(
       board_id=env.ICEE_NOTICE_BOARD_ID,
       base_url="https://icee.smu.ac.kr/icee/community/notice.do",
       params={
           "mode": "list",
           "articleLimit": 50,
           "article.offset": 0
       },
       interval= env.ICEE_NOTICE_INTERVAL,
       campus="seoul"
   ),   
   "swai_notice": ScraperConfig(
       board_id=env.SWAI_NOTICE_BOARD_ID,
       base_url="https://swai.smu.ac.kr/bbs/board.php",
       params={
            "bo_table": "07_01", 
       },
       interval= env.SWAI_NOTICE_INTERVAL,
       campus="seoul"
   ),
   "sm_career": ScraperConfig(
       board_id=env.SMCAREER_NOTICE_BOARD_ID,
       base_url="https://smcareer.smu.ac.kr/_user/capability/info/khs/do.asp",
       params={

       },
       interval= env.SMCAREER_NOTICE_INTERVAL,
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