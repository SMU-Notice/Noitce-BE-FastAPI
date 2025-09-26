# from typing import List, Dict
# from ocr_pipeline.post_process.timeline.cluster_date_blocks import cluster_date_blocks
# from ocr_pipeline.post_process.timeline.extract_timeline_object import extract_timeline_object
# import logging

# logger = logging.getLogger(__name__)

# # 타임라인 섹션 후처리 
# def timeline_post_process(
#     section: List[Dict]) -> str:
    
#     logger.debug("[timeline] 타임라인 후처리 시작")
    
#     try:
#         avg_h = sum(b["h"] for b in section) / len(section)
        
#         #글자 크기 기반 임계값 설정
#         dx_threshold = min(max(int(avg_h * 4.5), 50), 150)
#         dy_threshold = min(max(int(avg_h * 0.8), 10), 25)
        
#         date_clusters = cluster_date_blocks(section, dx_threshold, dy_threshold)
#         logger.debug(f"[timeline] 날짜 블록 클러스터링 완료 - {len(date_clusters)}개")
        
#         timeline_objects = [extract_timeline_object(cluster, section) for cluster in date_clusters]
#         logger.debug("[timeline] 타임라인 객체 추출 완료")
        
#         timeline = []
#         for obj in timeline_objects:
#             item = obj['date']
#             if obj['title']:
#                 item += "\n" + obj["title"]
#             if obj["desc"]:
#                 item += "\n" + obj['desc']
#             timeline.append(item)
        
#         logger.debug("[timeline] 타임라인 후처리 완료")
#         return "\n\n".join(timeline)

#     except Exception as e:
#         logger.debug("[timeline] 타임라인 후처리 중 예외 발생", exc_info=True)
#         raise
    
