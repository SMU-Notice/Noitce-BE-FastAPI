import numpy as np
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

def calculate_dynamic_table_tolerance(blocks: List[Dict]) -> int:
    """
    OCR 블록들의 평균 너비를 기반으로 X 클러스터링 tolerance를 동적으로 계산
    """
    widths = [b.get("w", 0) for b in blocks if b.get("w", 0) > 0]
    if not widths:
        return 30

    avg_width = np.mean(widths)

    # 해상도 및 종횡비 보정
    sample = next((b for b in blocks if "image_width" in b and "image_height" in b), None)
    if sample:
        image_width = sample["image_width"]
        image_height = sample["image_height"]
        aspect_ratio = image_height / image_width if image_width > 0 else 1.0

        aspect_factor = 1.0
        if aspect_ratio > 1.3:
            aspect_factor += min((aspect_ratio - 1.3) * 0.2, 0.3)
        elif aspect_ratio < 0.8:
            aspect_factor -= min((0.8 - aspect_ratio) * 0.2, 0.2)

        resolution_factor = 1.0
        if image_width >= 1000:
            resolution_factor += 0.05
        elif image_width <= 600:
            resolution_factor -= 0.05

        tolerance = avg_width * 0.8 * aspect_factor * resolution_factor
    else:
        tolerance = avg_width * 0.8

    return int(min(max(float(tolerance), 15), 80))


def get_x_pattern(line: List[Dict], tolerance: int) -> List[int]:
    """
    한 줄의 블록들에서 X 기준으로 열 클러스터 추출
    """
    xs = sorted([block["x"] for block in line])
    if not xs:
        return []

    clusters = [xs[0]]
    for x in xs[1:]:
        if abs(x - clusters[-1]) > tolerance:
            clusters.append(x)
    return clusters


def get_section_x_patterns(section: List[Dict], y_tolerance: int = 20, x_tolerance: int = 30) -> List[List[int]]:
    """
    섹션 내부를 행 단위로 나눈 후 각 행에서 X 패턴(열 좌표)을 추출
    """
    section = sorted(section, key=lambda b: b["y"] + b.get("h", 0) // 2)
    lines = []
    current_line = [section[0]]

    for i in range(1, len(section)):
        prev = section[i - 1]
        curr = section[i]
        prev_cy = prev["y"] + prev.get("h", 0) // 2
        curr_cy = curr["y"] + curr.get("h", 0) // 2

        if abs(curr_cy - prev_cy) > y_tolerance:
            lines.append(current_line)
            current_line = [curr]
        else:
            current_line.append(curr)

    lines.append(current_line)
    return [get_x_pattern(line, tolerance=x_tolerance) for line in lines]


def score_table_like_similarity(s1: List[Dict], s2: List[Dict], x_tolerance: int) -> float:
    """
    두 섹션이 테이블처럼 유사한 구조를 가졌는지 점수로 평가 (0.0 ~ 1.0)
    """
    patterns1 = get_section_x_patterns(s1, x_tolerance=x_tolerance)
    patterns2 = get_section_x_patterns(s2, x_tolerance=x_tolerance)

    if len(patterns1) < 2 or len(patterns2) < 2:
        return 0.0

    lengths1 = [len(p) for p in patterns1]
    lengths2 = [len(p) for p in patterns2]

    avg1, avg2 = np.mean(lengths1), np.mean(lengths2)
    std_combined = np.std(lengths1 + lengths2)

    score = 1.0
    if abs(avg1 - avg2) > 2:
        score -= 0.5
    if std_combined > 2.0:
        score -= 0.3

    return max(score, 0.0)


def merge_table_like_sections(sections: List[List[Dict]]) -> List[List[Dict]]:
    """
    섹션들 중 테이블로 의심되는 인접 섹션을 병합 (유사성 점수 기반)
    """
    logger.info("[table] 테이블 유사 섹션 병합 시작")
    merged = []
    i = 0

    try:
        all_blocks = [b for s in sections for b in s]
        x_tolerance = calculate_dynamic_table_tolerance(all_blocks)

        while i < len(sections):
            current = sections[i]
            j = i + 1
            while j < len(sections):
                score = score_table_like_similarity(current, sections[j], x_tolerance)
                if score >= 0.7:
                    logger.debug(f"[table] 병합: 섹션 {i} + {j}, score={score:.2f}")
                    current += sections[j]
                    j += 1
                else:
                    break
            merged.append(current)
            i = j

    except Exception as e:
        logger.exception("[table] 병합 도중 오류 발생")

    logger.info(f"[table] 병합 완료 → 총 섹션 수: {len(merged)}")
    return merged
