# from typing import List, Dict
# from ocr_pipeline.classifier.table.group_rows_by_y import group_rows_by_y
# from ocr_pipeline.classifier.timeline.contains_date import contains_date_in_text

# #날짜 블록과 인접한 텍스트 블록이 있는지 확인
# def find_date_text_pairs(
#     section: List[Dict],
#     y_tolerance: int) -> int:
    
#     rows = group_rows_by_y(section, y_tolerance)
#     pair_count = 0
    
#     for i, row in enumerate(rows):
#         #현재 행의 전체 텍스트
#         row_text = "".join(block["text"] for block in row)
#         if contains_date_in_text(row_text):
#             # 같은 행에 인접한 텍스트 블록이 있는지 확인
#             has_same_row_text = any(not contains_date_in_text(block["text"]) for block in row)
            
#             # 다음 행에 인접한 텍스트 블록이 있는지 확인
#             has_next_row_text = False
#             if i + 1 < len(rows):
#                 next_row = rows[i + 1]
#                 has_next_row_text = any(not contains_date_in_text(block["text"]) for block in next_row)
    
#             if has_same_row_text or has_next_row_text:
#                 pair_count += 1
    
#     return pair_count