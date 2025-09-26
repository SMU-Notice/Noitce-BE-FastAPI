from typing import List, Dict
from .is_simple_column import is_simple_column
from .simple_column_post_process import simple_column_post_process
from .complex_column_post_process import complex_column_post_process
import logging

logger = logging.getLogger(__name__)

def column_post_process(
    section: List[Dict],
    text_join_Delim: str = " ",
    classifier_args: Dict[str, Dict] = {},
    post_process_args: Dict[str, Dict] = {}
) -> List[str]:
    """
    컬럼 섹션을 단순/복잡 구조로 나누어 적절한 방식으로 후처리
    """
    try:
        if is_simple_column(section):
            logger.debug("[column] 단순 컬럼으로 판단 → 클러스터 기반 처리")
            return simple_column_post_process(section, text_join_Delim)
        else:
            logger.debug("[column] 복잡 컬럼으로 판단 → 내부 분석 및 타입 분기 처리")
            return complex_column_post_process(section, 
                                               classifier=classifier_args,
                                               post_process_config=post_process_args)
    except Exception as e:
        logger.exception("[column] 컬럼 후처리 중 예외 발생")
        return ["후처리 실패"]