from .table.table_classifier import score_table_section
from .column.column_classifier import score_column_section
# from .timeline.timeline_classifier import score_timeline_section
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

#4. 각 섹션들의 타입 판별
def classify_section_type(
    section: List[Dict],
    config: Dict[str, Dict] = {},
    min_score_threshold: float = 0.25,
    min_score_gap: float = 0.05
    ) -> str:
    logger.debug("섹션 타입 판별 시작")

    table_score = score_table_section(section, **config.get("table", {}))
    column_score = score_column_section(section, **config.get("column", {}))
    # timeline_score = score_timeline_section(section, **config.get("timeline", {}))

    logger.debug(f"[score] table: {table_score:.2f}, column: {column_score:.2f}")

    scores = {
        "table": table_score,
        "column": column_score,
        # "timeline": timeline_score,
    }

    best_type, best_score = max(scores.items(), key=lambda x: x[1])
    second_type, second_score = sorted(scores.items(), key=lambda x: x[1], reverse=True)[1]
    
    best_type, best_score = max(scores.items(), key=lambda x: x[1])
    second_type, second_score = sorted(scores.items(), key=lambda x: x[1], reverse=True)[1]

    # 1. 둘 다 기준 미달이면 → text
    if best_score < min_score_threshold and second_score < min_score_threshold:
        logger.debug(f"[result] table/column 모두 기준 미달 → text로 판별")
        return "text"

    # 2. 점수 차 작고, table이 일정 수준 이상일 때만 → table 우선 보정
    if abs(table_score - column_score) < 0.05:
        if table_score >= 0.30 and column_score > min_score_threshold:
            logger.debug(f"[result] 점수 차 작고 table 점수 신뢰도 높음 → table 우선")
            return "table"
        elif column_score >= 0.30 and table_score > min_score_threshold:
            logger.debug(f"[result] 점수 차 작고 column 점수 신뢰도 높음 → column 우선")
            return "column"

    # 3. 점수 차 작고, 둘 다 낮은 점수면 → text
    if abs(best_score - second_score) < min_score_gap:
        if best_score < (min_score_threshold + 0.1) and second_score < (min_score_threshold + 0.1):
            logger.debug(f"[result] 점수 차 작고 둘 다 애매한 점수 → text로 판별")
            return "text"

    # 4. 점수 차와 무관하게 best_type이 기준 이상이면 그대로 반환
    if best_score > min_score_threshold:
        logger.debug(f"[result] best type({best_type}) 점수 충분 → {best_type}로 판별")
        return best_type

    # 5. fallback: text
    logger.debug(f"[result] fallback → text로 판별")
    return "text"
    