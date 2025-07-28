# from typing import List, Dict

# def extract_timeline_object(cluster: List[Dict], section: List[Dict]) -> Dict:
    
#     #날짜 텍스트 추출
#     date_text = "".join(block["text"] for block in sorted(cluster, key = lambda b: b["x"]))
    
#     #날짜 블록의 평균 Y좌표
#     date_y = sum(b["y"] for b in cluster) / len(cluster)
#     #날짜 블록의 평균 높이 -> 글자 크기에 따른 반영
#     avg_h = sum(b["h"] for b in cluster) / len(cluster)
    
#     #날짜 기준 위/아래 인접 판단
#     dy_thresh = min(max(int(avg_h * 0.8), 10), 25)
    
#     #날짜 블록을 제외한 나머지 블록
#     others = [b for b in section if b not in cluster]
    
#     above = [b for b in others if b["y"] < date_y - dy_thresh]
#     below = [b for b in others if b["y"] > date_y + dy_thresh]
    
#     title = ""
#     desc_blocks = above + below
    
#     #날짜 위의 텍스트 중 제목으로 예상되는 부분은 title에 추가 및 설명 블록에서 제거
#     if above:
#         closest = min(above, key= lambda b: abs(b["y"] - date_y))
#         if len(closest["text"].strip()) <= 20 and closest["h"] <= avg_h * 1.2:
#             title = closest["text"].strip()
#             desc_blocks.remove(closest)
    
#     desc_blocks_sorted = sorted(desc_blocks, key=lambda b: b["y"])
#     desc = " ".join(b["text"] for b in desc_blocks_sorted if b["text"].strip())
    
#     return {
#         "title": title,
#         "desc": desc,
#         "date": date_text.strip()
#     }