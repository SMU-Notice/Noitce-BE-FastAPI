import numpy as np
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


def calculate_dynamic_column_tolerance(blocks: List[Dict]) -> int:
    """
    OCR 블록들의 평균 너비 + 해상도 및 종횡비 기반으로 컬럼 클러스터링 tolerance를 동적으로 계산
    """
    widths = [b.get("w", 0) for b in blocks if b.get("w", 0) > 0]
    if not widths:
        return 40
    avg_width = np.mean(widths)
    base_tolerance = avg_width * 1.2

    # 해상도 및 종횡비 기반 보정
    sample_block = next((b for b in blocks if "image_width" in b and "image_height" in b), None)
    if not sample_block:
        tolerance = base_tolerance
    else:
        image_width = sample_block["image_width"]
        image_height = sample_block["image_height"]
        aspect_ratio = image_height / image_width if image_width > 0 else 1.0

        # 종횡비 보정 (과도한 보정 방지)
        aspect_factor = 1.0
        if aspect_ratio > 1.3:
            aspect_factor += min((aspect_ratio - 1.3) * 0.1, 0.15)
        elif aspect_ratio < 0.8:
            aspect_factor -= min((0.8 - aspect_ratio) * 0.1, 0.1)

        # 해상도 보정
        resolution_factor = 1.0
        if image_width >= 1000:
            resolution_factor += 0.03
        elif image_width <= 600:
            resolution_factor -= 0.03

        tolerance = base_tolerance * aspect_factor * resolution_factor
    return int(min(max(float(tolerance), 25), 100))

def cluster_x_positions(blocks: List[Dict], tolerance: int) -> List[int]:
    x_centers = sorted([b["x"] + b.get("w", 0) // 2 for b in blocks])
    if not x_centers:
        return []

    clusters = [x_centers[0]]
    for x in x_centers[1:]:
        if abs(x - clusters[-1]) > tolerance:
            clusters.append(x)
    return clusters

def score_column_like_similarity(s1: List[Dict], s2: List[Dict], tolerance: int) -> float:
    """
    두 섹션이 컬럼 구조로 유사한지 점수 반환 (0~1)
    - 컬럼 수 유사
    - 컬럼 간 블록 수 균형
    """
    clusters1 = cluster_x_positions(s1, tolerance)
    clusters2 = cluster_x_positions(s2, tolerance)

    if len(clusters1) <= 1 or len(clusters2) <= 1:
        return 0.0

    col_diff = abs(len(clusters1) - len(clusters2))
    col_score = 1.0 if col_diff == 0 else 0.7 if col_diff == 1 else 0.0

    blocks_per_col_1 = len(s1) / max(len(clusters1), 1)
    blocks_per_col_2 = len(s2) / max(len(clusters2), 1)
    balance_diff = abs(blocks_per_col_1 - blocks_per_col_2)
    balance_score = 1.0 if balance_diff < 2 else 0.5 if balance_diff < 4 else 0.0

    return round((col_score * 0.6 + balance_score * 0.4), 2)


def merge_column_like_sections(sections: List[List[Dict]]) -> List[List[Dict]]:
    """
    섹션들 중 컬럼으로 의심되는 인접 섹션을 병합 (유사성 점수 기반)
    """
    logger.info("[column] 컬럼 유사 섹션 병합 시작")
    merged = []
    i = 0

    try:
        all_blocks = [b for s in sections for b in s]
        tolerance = calculate_dynamic_column_tolerance(all_blocks)

        while i < len(sections):
            current = sections[i]
            j = i + 1
            while j < len(sections):
                if len(current) < 3 or len(sections[j]) < 3:
                    break

                score = score_column_like_similarity(current, sections[j], tolerance)
                if score >= 0.85:
                    logger.debug(f"[column] 병합: 섹션 {i} + {j}, score={score:.2f}")
                    current += sections[j]
                    j += 1
                else:
                    break
            merged.append(current)
            i = j

    except Exception as e:
        logger.exception("[column] 병합 도중 오류 발생")

    logger.info(f"[column] 병합 완료 → 총 섹션 수: {len(merged)}")
    return merged