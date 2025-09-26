from typing import List, Dict
from app.board.infra.ocr.ocr_pipeline.classifier.column.cluster_blocks import cluster_blocks_by_x
from app.board.infra.ocr.ocr_pipeline.classifier.classify_section_type import classify_section_type
from app.board.infra.ocr.ocr_pipeline.layout_analysis.split_sections import split_sections_by_y_gap
import logging
logger = logging.getLogger(__name__)

def complex_column_post_process(
    blocks: List[Dict],
    classifier: Dict[str, Dict],
    post_process_config: Dict[str, Dict]
) -> List[str]:
    
    from ..post_process_section_by_type import post_process_section_by_type

    """
    복잡한 컬럼 섹션을 1-depth로 컬럼 단위로 나눠서 처리.
    내부 구조가 복잡하더라도 재귀 없이 처리한다.
    """

    logger.debug("[column] 복잡 컬럼 후처리 시작")
    try:
        # 1. x 좌표 기반 컬럼 클러스터링
        avg_width = sum(b["w"] for b in blocks) / max(len(blocks), 1)
        section_width = max(b["x"] for b in blocks) - min(b["x"] for b in blocks)
        x_gap_threshold = min(max(int(avg_width * 1.2), 15), int(section_width * 0.06))

        column_bins = cluster_blocks_by_x(blocks, x_gap_threshold)
        logger.debug(f"[column] 클러스터링 결과 → {len(column_bins)}개 컬럼")

        final_columns: List[str] = []

        # 2. 각 컬럼별 내부 구조 분석 및 후처리
        for col_blocks in column_bins:
            inner_sections = split_sections_by_y_gap(
                col_blocks,
                min_section_height=20,
                max_sections=20
            )

            column_texts = []
            for inner in inner_sections:
                section_type = classify_section_type(inner, classifier)

                if section_type == "column":
                    logger.debug("[column 내부] nested column → text로 처리")
                    section_type = "text"

                result = post_process_section_by_type(inner, section_type, classifier, post_process_config)

                if isinstance(result, list) and all(isinstance(r, list) for r in result):
                    column_texts.append("\n".join(["\t".join(row) for row in result]))
                elif isinstance(result, list):
                    column_texts.extend(str(r).strip() for r in result)
                else:
                    column_texts.append(str(result).strip())

            final_columns.append("\n".join(column_texts))

        logger.debug("[column] 복잡 컬럼 후처리 완료")
        return final_columns

    except Exception as e:
        logger.exception("[column] 복잡 컬럼 후처리 중 예외 발생")
        return ["후처리 실패"]