from typing import List, Dict
import logging
import numpy as np
from ..config.block_sort_config import block_sort_config

logger = logging.getLogger(__name__)

#3. OCR 블록들을 Y좌표 기준 정렬 -> 줄 내에서는 X 좌표 기준 정렬
def sort_blocks(blocks: List[Dict], config: Dict = block_sort_config) -> List[Dict]:
    
    #Y 기준으로 가까운 블록끼리 같은 줄로 판단 (동적 마진 적용)
    
    try:
        margin = config.get("y_overlap_margin", 5)
        min_h = config.get("min_line_height", 5)
        max_h = config.get("max_line_height", 100)
        margin_ratio = config.get("dynamic_margin_ratio", 0.5)

        # 블록 높이 필터링 및 평균 계산
        heights = [block.get("h", 0) for block in blocks if min_h <= block.get("h", 0) <= max_h]
        avg_height = np.mean(heights) if heights else 20

        lines: List[List[Dict]] = []

        for block in sorted(blocks, key=lambda b: b["y"]):
            y1 = block["y"]
            y2 = y1 + block.get("h", 0)
            placed = False

            for line in lines:
                line_ys = [b["y"] for b in line]
                line_heights = [b["h"] for b in line]
                line_min = min(line_ys)
                line_max = max(y + h for y, h in zip(line_ys, line_heights))
                line_range = line_max - line_min
                dynamic_margin = max(margin, line_range * margin_ratio)

                if y2 >= line_min - dynamic_margin and y1 <= line_max + dynamic_margin:
                    line.append(block)
                    placed = True
                    break

            if not placed:
                lines.append([block])

        sorted_lines = [sorted(line, key=lambda b: b["x"]) for line in lines]
        sorted_blocks = [b for line in sorted_lines for b in line]

        logger.info(f"정렬 완료 (라인 기반): 총 {len(sorted_blocks)}개 블록, {len(sorted_lines)}줄")
        return sorted_blocks

    except Exception as e:
        logger.debug("정렬 중 예외 발생", exc_info=True)
        raise
