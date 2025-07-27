from .table.table_post_process import table_post_process
from .column.column_post_process import column_post_process
from .text.text_post_process import text_post_process
from typing import List, Dict, Union
import logging

logger = logging.getLogger(__name__)

# 섹션 타입에 따라 해당 후처리 로직 호출
def post_process_section_by_type(
    section: List[Dict],
    section_type: str,
    classifier_config: Dict[str, Dict] = {},
    post_process_config: Dict[str, Dict] = {}
) -> Union[str, List[str], List[List[str]]]:
    
    logger.debug(f"섹션 후처리 시작 - 타입: {section_type}")

    try:
        if section_type == "table":
            # 테이블로 처리 (List[List[str]]] 타입으로 반환)
            return table_post_process(section, **post_process_config.get("table", {}))
        
        elif section_type == "column":
            # 컬럼으로 처리 (List[str] 타입으로 반환)
            return column_post_process(
                            section,
                            text_join_Delim=post_process_config.get("column", {}).get("text_join_Delim", " "),
                            classifier_args=classifier_config,
                            post_process_args=post_process_config
                        )            
        else:
            return text_post_process(section)
        
    except Exception as e:
        logger.error(f"섹션 후처리 실패 - 타입: {section_type}, 에러: {e}")
        return "후처리 실패"
