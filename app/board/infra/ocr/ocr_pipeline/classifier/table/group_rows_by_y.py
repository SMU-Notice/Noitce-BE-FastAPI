from typing import List, Dict

def group_rows_by_y(section: List[Dict], y_tolerance: int) -> List[List[Dict]]:
    rows = []

    def get_center_y(block):
        return block["y"] + block.get("h", 0) // 2

    # y 중심 기준 정렬
    sorted_blocks = sorted(section, key=get_center_y)

    for block in sorted_blocks:
        b_cy = get_center_y(block)
        placed = False

        for row in rows:
            row_cys = [get_center_y(b) for b in row]
            avg_cy = sum(row_cys) / len(row_cys)

            if abs(b_cy - avg_cy) <= y_tolerance:
                row.append(block)
                placed = True
                break

        if not placed:
            rows.append([block])

    return rows
