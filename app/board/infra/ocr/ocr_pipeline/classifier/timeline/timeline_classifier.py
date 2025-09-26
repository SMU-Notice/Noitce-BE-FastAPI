# from typing import List, Dict
# from ocr_pipeline.classifier.timeline.find_date_text_pairs import find_date_text_pairs
# import numpy as np
# import logging

# logger = logging.getLogger(__name__)

# def get_y_tolerance_dynamic(section: List[Dict], ratio: float = 0.8, min_tol: int = 10, max_tol: int = 25) -> int:
#     heights = [block["h"] for block in section]
#     avg_h = np.mean(heights) if heights else 15
#     return min(max(int(avg_h * ratio), min_tol), max_tol)

# # 4-3. 타임라인 타입 판별
# def score_timeline_section(section: List[Dict],
#                         min_pairs: int
#                         ) -> float:
    
#     logger.debug("[timeline] 타임라인 섹션 판별 시작")
    
#     try:
#         #y_tolerance 임계값
#         y_tolerance = get_y_tolerance_dynamic(section)
#         #정규표현식 기반 날짜 감지 + 날짜 블록과 인접한 텍스트 블록 존재 유무로 판별
#         pairs = find_date_text_pairs(section, y_tolerance)
        
#         score = min(pairs / 5.0, 1.0)
#         logger.debug(f"[timeline]  날짜-텍스트 쌍 수: {pairs}, (기준: {min_pairs})")
        
#         return round(score, 2)

#     except Exception as e: 
#         logger.debug("[timeline] 타임라인 판별 중 예외 발생", exc_info=True)
#         raise