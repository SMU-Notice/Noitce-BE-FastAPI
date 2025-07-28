# from typing import List, Dict
# from ocr_pipeline.classifier.timeline.contains_date import contains_date_in_text
# import numpy as np

# #섹션에서 날짜 블록 찾기
# def cluster_date_blocks(section: List[Dict],
#                         dx_threshold: int,
#                         dy_threshold:int) -> List[List[Dict]]:
#     date_blocks = []
#     used = set()
    
#     heights = [block["h"] for block in section]
#     avg_h = np.mean(heights)
    
#     for i, block in enumerate(section):
#         if i in used:
#             continue
#         text = block["text"]
#         if contains_date_in_text(text):
#             cluster = [block]
#             used.add(i)
            
#             #주변 블록들도 함께 병합 
#             for j, other in enumerate(section):
#                 if j in used or i ==j:
#                     continue
#                 if contains_date_in_text(other["text"]):
#                     dx = abs(block["x"] - other["x"])
#                     dy = abs(block["y"] - other["y"])
#                     if dy < dy_threshold and dx < dx_threshold:
#                         cluster.append(other)
#                         used.add(j)
#             date_blocks.append(cluster)
                    
#     return date_blocks