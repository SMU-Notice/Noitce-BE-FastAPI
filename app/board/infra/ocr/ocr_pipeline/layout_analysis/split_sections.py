from typing import List, Dict, Optional
import logging
import numpy as np

logger = logging.getLogger(__name__)


from typing import List, Dict
import logging
import numpy as np

logger = logging.getLogger(__name__)

#섹션 분리에 쓰일 y 임계값 동적 계산
def calculate_adaptive_y_threshold(
    blocks: List[Dict],
    fallback: int = 25
) -> int:
    if not blocks:
        return fallback

    heights = [block.get("h", 0) for block in blocks if block.get("h", 0) > 0]
    if not heights:
        return fallback
    avg_height = np.mean(heights)

    # 블록에서 이미지 너비/높이 추출
    image_width = blocks[0].get("image_width", 1000)
    image_height = blocks[0].get("image_height", 1000)

    # 종횡비 보정
    aspect_ratio = image_height / image_width if image_width > 0 else 1.0
    aspect_factor = 1.0
    if aspect_ratio > 1.3:
        aspect_factor += min((aspect_ratio - 1.3) * 0.3, 0.4)
    elif aspect_ratio < 0.8:
        aspect_factor -= min((0.8 - aspect_ratio) * 0.3, 0.3)

    # 해상도 보정
    resolution_factor = 1.0
    if image_height >= 2000:
        resolution_factor += 0.1
    elif image_height <= 800:
        resolution_factor -= 0.1

    threshold = avg_height * 1.1 * aspect_factor * resolution_factor
    threshold = int(min(max(float(threshold), 30), 120))

    logger.debug(
        f"[threshold] 평균 높이: {avg_height:.1f}, 종횡비: {aspect_ratio:.2f}, "
        f"보정: a({aspect_factor:.2f}) * r({resolution_factor:.2f}), → y_threshold: {threshold}"
    )
    return threshold

#블록들을 줄 단위로 그룹핑
def group_blocks_into_lines(blocks: List[Dict], y_tolerance: int) -> List[List[Dict]]:
    lines: List[List[Dict]] = []
    sorted_blocks = sorted(blocks, key=lambda b: b["y"] + b.get("h", 0) // 2)

    for block in sorted_blocks:
        cy = block["y"] + block.get("h", 0) // 2
        matched = False

        for line in lines:
            ly = np.mean([b["y"] + b.get("h", 0) // 2 for b in line])
            if abs(cy - ly) <= y_tolerance:
                line.append(block)
                matched = True
                break

        if not matched:
            lines.append([block])

    return [sorted(line, key=lambda b: b["x"]) for line in lines]


def split_sections_by_y_gap(
    blocks: List[Dict],
    min_section_height: int = 50,
    max_sections: int = 10,
    y_threshold: Optional[int] = None
) -> List[List[Dict]]:
    """
    줄 단위 블록들을 Y 간격 기준으로 섹션으로 분리하며,
    - 종횡비, 해상도 기반 동적 y_threshold 자동 계산 (최초 1회)
    - 과도한 섹션 분리/병합 방지
    """
    try:
        if not blocks:
            return []

        # 최초 한 번만 동적 임계값 계산
        if y_threshold is None:
            y_threshold = calculate_adaptive_y_threshold(blocks)

        sections = []
        current_section = []

        y_tolerance = max(int(y_threshold * 0.51), 10)
        lines = group_blocks_into_lines(blocks, y_tolerance)

        for i, line in enumerate(lines):
            if not current_section:
                current_section.extend(line)
                continue

            prev_line = lines[i - 1]
            curr_line = line

            prev_y = np.mean([b["y"] + b.get("h", 0) // 2 for b in prev_line])
            curr_y = np.mean([b["y"] + b.get("h", 0) // 2 for b in curr_line])
            y_gap = curr_y - prev_y

            curr_sec_top = current_section[0]["y"]
            curr_sec_bottom = current_section[-1]["y"] + current_section[-1]["h"]
            curr_sec_height = curr_sec_bottom - curr_sec_top

            logger.debug(f"[split] 줄 간 중심 간격: {y_gap:.1f}, 기준: {y_threshold}")

            if (
                y_gap >= y_threshold and
                curr_sec_height >= min_section_height and
                len(current_section) >= 3  # 헤더만 따로 분리되는 것 방지
                ):
                logger.debug(f"[split] 섹션 분리 발생 (y_gap: {y_gap:.1f}, height: {curr_sec_height:.1f})")
                sections.append(current_section)
                current_section = list(line)
            else:
                current_section.extend(line)

        if current_section:
            sections.append(current_section)

        # 섹션 수가 너무 많으면 y_threshold를 1.3배로 늘려 재귀 재시도 (단, threshold는 유지되며 한 단계씩만 증가)
        if len(sections) > max_sections:
            new_threshold = int(y_threshold * 1.3)
            logger.warning(f"[split] 섹션 {len(sections)}개 → 과분할 감지. 임계값 완화 후 재시도 ({new_threshold})")
            return split_sections_by_y_gap(
                blocks,
                min_section_height,
                max_sections,
                y_threshold=new_threshold  # ← 증가된 값 유지
            )

        logger.info(f"[split] 줄 기반 섹션 분리 완료 - {len(sections)}개 섹션")
        return sections

    except Exception as e:
        logger.exception("줄 기반 섹션 분리 중 예외 발생")
        raise e
