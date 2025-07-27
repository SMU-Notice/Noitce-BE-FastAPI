# from typing import List, Dict
# from ocr_pipeline.classifier.table.group_rows_by_y import group_rows_by_y
# import re

# date_patterns = [
#     r"\d{4}\.\d{1,2}\.\d{1,2}",             #2025.06.20
#     r"\d{1,2}\.\d{1,2}",                    #06.20
#     r"\d{1,2}\/\d{1,2}",                    #06/20
#     r"\d{2,4}년\s?\d{1,2}월\s?\d{1,2}일",   #2025년 6월 20일
#     r"\d{1,2}월\s?\d{1,2}일",               #6월 20일
#     r"\d{1,2}\.\d{1,2}~\d{1,2}\.\d{1,2}"    #06.20~06.24
# ]

# #텍스트에 날짜가 포함되어 있는지 여부
# def contains_date_in_text(text: str) -> bool:
    
#     #text 안에서 p에 매칭되는 부분을 찾아내서 하나라도 있으면 True
#     return any(re.search(p, text) for p in date_patterns)

# #json 안에 여러 블록으로 나뉘어진 날짜 정보를 그룹화 및 검증
# def contains_date_in_section(
#     section: List[Dict],
#     y_tolerance: int) -> bool:
    
#     rows = group_rows_by_y(section, y_tolerance)
#     for row in rows:
#         joined_date = "".join(block["inferText"] for block in row)
#         if contains_date_in_text(joined_date):
#             return True
#     return False