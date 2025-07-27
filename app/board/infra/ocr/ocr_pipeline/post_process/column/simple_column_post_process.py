from typing import List, Dict
from app.board.infra.ocr.ocr_pipeline.classifier.column.cluster_blocks import cluster_blocks_by_x
from app.board.infra.ocr.ocr_pipeline.classifier.table.group_rows_by_y import group_rows_by_y
import logging

logger = logging.getLogger(__name__)

# 단순한 구조의 컬럼 섹션을 컬럼 단위로 텍스트 복원
def simple_column_post_process(
    section: List[Dict],
    text_join_Delim: str
) -> List[str]:

    logger.debug("[column] 컬럼 후처리 시작")

    try:
        # 섹션 내부 블록들의 평균 너비
        avg_width = sum(b["w"] for b in section) / max(len(section), 1)

        # 섹션 전체의 가로 너비
        section_width = max(b["x"] for b in section) - min(b["x"] for b in section)

        # 임계값 설정 (x 기준 클러스터링용)
        x_gap_threshold = min(max(int(avg_width * 1.5), 20), int(section_width * 0.1))

        # 1) 컬럼 클러스터링
        column_bins = cluster_blocks_by_x(section, x_gap_threshold)
        logger.debug(f"[column] 컬럼 클러스터링 완료 - {len(column_bins)}개")

        # 2) 각 컬럼 내부를 줄 단위로 묶고, 각 줄은 x 정렬
        columns = []
        for col_blocks in column_bins:
            avg_height = sum(b["h"] for b in col_blocks) / max(len(col_blocks), 1)
            y_tolerance = min(max(int(avg_height * 0.6), 10), 40)
            
            # 평균 높이 기반 동적 y_tolerance
            rows = group_rows_by_y(col_blocks, y_tolerance=y_tolerance)

            row_texts = []
            for row in rows:
                sorted_row = sorted(row, key=lambda b: b["x"])
                line = text_join_Delim.join(block["text"].replace("\n", " ").strip() for block in sorted_row)
                row_texts.append(line)
            column_text = "\n".join(row_texts)  # 줄 단위로 붙이기
            columns.append(column_text)

        logger.debug("[column] 컬럼 후처리 완료")
        return columns

    except Exception as e:
        logger.exception("[column] 컬럼 후처리 중 예외 발생")
        raise
