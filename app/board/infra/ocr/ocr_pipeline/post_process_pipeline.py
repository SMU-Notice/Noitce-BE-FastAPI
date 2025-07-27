from typing import List, Dict, cast
from .layout_analysis.block_extractor import extract_blocks_from_ocr_response
from .layout_analysis.sorted_block import sort_blocks
from .layout_analysis.split_sections import split_sections_by_y_gap, calculate_adaptive_y_threshold
from .layout_analysis.merge_sections.merge_table_like_sections import merge_table_like_sections
from .layout_analysis.merge_sections.merge_column_like_sections import merge_column_like_sections
from .classifier.classify_section_type import classify_section_type
from .post_process.post_process_section_by_type import post_process_section_by_type

import logging

logger = logging.getLogger(__name__)

def post_process_pipeline(
    ocr_response: Dict,
    section_classification_config: Dict[str, Dict],
    post_process_config: Dict[str, Dict]
    )-> List[str]:
    
    logger.info("전체 후처리 파이프라인 시작")
    
    # 1. OCR 응답(json)에서
    # 필요한 정보(bounding box, text, linebreak)를 담아 여러 블록으로 추출    
    
    logger.info("ocr 응답에서 텍스트 블록 추출")
    blocks = extract_blocks_from_ocr_response(ocr_response)
    logger.info(f"블록 추출 완료 - {len(blocks)}개")
    
    # 2. 블록 정렬 (Y -> X 정렬)
    # Y 우선 정렬, X는 보조
    logger.info("블록 정렬 시작")
    sorted_blocks = sort_blocks(blocks)
    logger.info("블록 정렬 완료")
    
    # 3. Y 간격 기반 섹션 분리
    logger.info("Y간격 기반 섹션 분리 시작")
    y_gap_threshold = calculate_adaptive_y_threshold(sorted_blocks)
    sections = split_sections_by_y_gap(sorted_blocks, y_gap_threshold)
    logger.info(f"섹션 분리 완료 - {len(sections)}개 ")
    
    # 3.5 분리된 섹션에서 테이블, 컬럼으로 의심되는 섹션들 병합
    logger.info("테이블/컬럼 병합 시작")
    sections = merge_table_like_sections(sections)
    sections = merge_column_like_sections(sections)
    logger.info(f"병합 후 섹션 수: {len(sections)}개")
    
    # 4. 섹션별 타입 분류
    logger.info("섹션 타입 분류 시작")
    sections_with_type = []
    for section in sections:
        section_type = classify_section_type(section, section_classification_config)
        sections_with_type.append({
            "blocks": section,
            "type": section_type
        })
    logger.info(
        f"타입 분류 완료 - 테이블: {sum(s['type'] == 'table' for s in sections_with_type)}, "
        f"컬럼: {sum(s['type'] == 'column' for s in sections_with_type)}, "
        # f"타임라인: {sum(s['type'] == 'timeline' for s in sections_with_type)}, "
        f"텍스트: {sum(s['type'] == 'text' for s in sections_with_type)}"
    )
    
    # 5. 타입별 후처리
    logger.info("섹션별 후처리 시작")
    results = []
    for idx, section in enumerate(sections_with_type):
        try:
            result = post_process_section_by_type(section["blocks"], section["type"], section_classification_config, post_process_config)

            # ✅ 후처리 결과 문자열화
            if section["type"] == "table":
                # 테이블: 행 단위 줄바꿈 + 열은 탭 또는 파이프(|)로 구분
                stringified = "\n".join(["\t".join(row) for row in result])
                results.append(stringified)

            elif section["type"] == "column":
                # 컬럼: 각 컬럼을 줄 단위로 출력, 컬럼 간에는 빈 줄
                column_lines = cast(List[str], result)
                stringified = "\n".join(line.strip() for line in column_lines)
                results.append(stringified)

            else:
                # 일반 텍스트 그대로
                results.append(result)
        except Exception as e:
            logger.error(f"섹션 {idx} ({section['type']}) 후처리 실패: {e}", exc_info=True)
            fallback = " ".join(block["text"].strip() for block in section["blocks"])
            results.append(fallback)

    logger.info("전체 후처리 완료")
    return results


