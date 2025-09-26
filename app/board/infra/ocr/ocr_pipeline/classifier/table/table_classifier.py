import numpy as np
from typing import List, Dict
from .group_rows_by_y import group_rows_by_y
import logging

logger = logging.getLogger(__name__)

def score_table_section(
    section: List[Dict],
    overlap_ratio_threshold: float,
    min_rows: int,
    colspan_check_enabled: bool
) -> float:
    logger.debug("[table] 테이블 섹션 판별 시작")

    try:
        
        #모든 블록들의 평균 높이
        avg_height = sum(b["h"] for b in section) / max(len(section), 1)
        #글자 크기에 따른 임계값 설정
        y_tolerance = min(max(int(avg_height * 0.8), 6), 20)
        
        rows = group_rows_by_y(section, y_tolerance)

        if len(rows) < min_rows:
            logger.debug(f"[table] 행 수 부족: {len(rows)} < {min_rows}")
            return 0.0

        # 1. 행 내 x 정렬 기준 분석
        row_x_list = [sorted(block["x"] for block in row) for row in rows if len(row) >= 2]
        row_x_diffs = [np.diff(xs) for xs in row_x_list if len(xs) >= 2]

        all_diffs = np.concatenate(row_x_diffs) if row_x_diffs else np.array([])
        avg_std = np.std(all_diffs) if len(all_diffs) > 0 else 999
        avg_diff = np.mean(all_diffs) if len(all_diffs) > 0 else 1
        std_threshold = min(max(int(avg_diff * 0.25), 5), 60)

        if avg_std < std_threshold * 0.6:
            row_std_score = 1.0
        elif avg_std < std_threshold * 1.2:
            row_std_score = 0.5
        else:
            row_std_score = 0.2

        # 2. 행 간 x 좌표 유사성 (overlap)
        overlap_ratios = []
        for i in range(len(row_x_list)):
            for j in range(i + 1, len(row_x_list)):
                set_i = set(row_x_list[i])
                set_j = set(row_x_list[j])
                union = set_i | set_j
                if union:
                    ratio = len(set_i & set_j) / len(union)
                    overlap_ratios.append(ratio)
        avg_overlap = np.mean(overlap_ratios) if overlap_ratios else 0.0

        if avg_overlap > 0.6:
            overlap_score = 1.0
        elif avg_overlap > 0.4:
            overlap_score = 0.4
        elif avg_overlap > 0.2:
            overlap_score = 0.1
        else:
            overlap_score = 0.0

        # 3. 셀 너비 표준편차 (너비 균형)
        all_widths = [block["w"] for row in rows for block in row]
        width_std = np.std(all_widths) if all_widths else 0.0
        
        if width_std < 100:
            width_std_score = 1.0
        elif width_std < 150:
            width_std_score = 0.7
        else:
            width_std_score = 0.2

        # 4. colspan 감지 (선택적)
        colspan_detected = False
        colspan_score = 0.0
        if colspan_check_enabled:
            max_cells_per_row = max(len(row) for row in rows)
            row_widths = [sum(block["w"] for block in row) for row in rows]
            avg_row_width = np.mean(row_widths) if row_widths else 0

            for row in rows:
                widths = [block["w"] for block in row]
                if (
                    len(row) <= max_cells_per_row - 2 and
                    sum(widths) > avg_row_width * 1.5 and
                    np.std(widths) > np.mean(widths) * 0.5
                ):
                    colspan_detected = True
                    colspan_score = 0.3
                    break

        # 5. 최종 점수 계산
        final_score = round((
            row_std_score * 0.4 +
            overlap_score * 0.3 +
            width_std_score * 0.2 +
            colspan_score * 0.1
        ), 2)
        
        # 감점 조건: 정렬 나쁨 + 오버랩 거의 없음
        if avg_std > 60 and avg_overlap < 0.1:
            if avg_std > 100 and width_std < 80 and len(rows) >= 4:
                logger.debug("[table] 구조 정렬 나쁘지만 셀 균형 좋아서 score 보정")
                final_score = min(max(final_score, 0.35), 0.45)
            else:
                logger.debug("[table] 정렬 나쁘고 오버랩 없음 → 테이블 아님 감점")
                final_score = min(final_score, 0.2)

        # 최종 점수에 상한 설정 (어정쩡한 구조 방지)
        if final_score > 0.6 and avg_std > 70 and avg_overlap < 0.3:
            logger.debug("[table] 과도한 점수 제한 적용")
            final_score = 0.55

        logger.debug(
            f"[table] 평균 std: {avg_std:.2f}, 평균 overlap: {avg_overlap:.2f}, "
            f"너비 std: {width_std:.2f}, colspan: {colspan_detected}, 최종 score: {final_score:.2f}"
        )

        return final_score

    except Exception as e:
        logger.exception("[table] 테이블 판별 중 예외 발생")
        return 0.0
