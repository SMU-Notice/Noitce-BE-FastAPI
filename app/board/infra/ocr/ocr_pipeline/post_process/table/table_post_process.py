from typing import List, Dict
from app.board.infra.ocr.ocr_pipeline.classifier.table.group_rows_by_y import group_rows_by_y
from .align_blocks_to_columns import align_blocks_to_columns
import logging

logger = logging.getLogger(__name__)

def table_post_process(
    section: List[Dict],
    max_iterations: int
) -> List[List[str]]: 

    logger.debug("[table] 테이블 후처리 시작")

    try:
        # 평균 블록 높이 계산
        avg_height = sum(b["h"] for b in section) / max(len(section), 1)

        # 임계값 계산
        y_tolerance = min(max(int(avg_height * 0.8), 6), 20)
        x_tolerance = min(max(int(avg_height * 2.0), 25), 70)
        std_threshold = min(max(int(avg_height * 0.4), 3), 20)

        # 1단계: 행 그룹핑
        rows = group_rows_by_y(section, y_tolerance)
        logger.debug(f"[table] 행 그룹핑 완료 - {len(rows)}행")

        # 2단계: 열 클러스터링 및 정렬 수렴
        table_blocks = align_blocks_to_columns(rows, x_tolerance, std_threshold, max_iterations)
        logger.debug(f"[table] 열 정렬 및 클러스터링 완료 - {len(table_blocks)}행")

        # 3단계: 셀 내 텍스트 정리 및 중첩 리스트로 반환
        table_lines: List[List[str]] = []

        for row in table_blocks:
            cell_texts = []
            for cell_blocks in row:
                if not cell_blocks:
                    cell_texts.append("")
                    continue
                sorted_cell = sorted(cell_blocks, key=lambda b: b["aligned_x"])
                raw_text = " ".join(b["text"] for b in sorted_cell if b.get("text"))
                cleaned_text = raw_text.replace("\n", " ").strip()
                cell_texts.append(cleaned_text)
            table_lines.append(cell_texts)  #각 행은 리스트로 추가

        logger.debug("테이블 요약용 후처리 완료")
        return table_lines  #중첩 리스트 반환

    except Exception as e:
        logger.exception("[table] 테이블 후처리 중 예외 발생")
        raise
