from typing import List, Dict
import numpy as np

# 컬럼으로 판단된 섹션을 컬럼으로 분리
def cluster_blocks_by_x(section: List[Dict], x_gap_threshold: float) -> List[List[Dict]]:
    """
    블록들을 x 중심 기준으로 IQR 기반 클러스터링하여 컬럼 후보로 나눔
    """
    if not section:
        return []

    sorted_blocks = sorted(section, key=lambda b: b["x"] + b["w"] // 2)
    centers = [b["x"] + b["w"] // 2 for b in sorted_blocks]

    center_diffs = np.diff(centers)
    q1 = np.percentile(center_diffs, 25)
    q3 = np.percentile(center_diffs, 75)
    iqr = q3 - q1

    avg_width = np.mean([b["w"] for b in section])
    adaptive_gap = np.clip(iqr * 1.5, avg_width * 0.8, avg_width * 2.5)

    column_bins: List[List[Dict]] = [[sorted_blocks[0]]]

    for i, block in enumerate(sorted_blocks[1:], 1):
        curr_center = centers[i]
        prev_center = centers[i - 1]

        if abs(curr_center - prev_center) <= adaptive_gap:
            column_bins[-1].append(block)
        else:
            column_bins.append([block])

    return column_bins

    