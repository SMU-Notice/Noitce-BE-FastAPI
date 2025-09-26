
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

def text_post_process(blocks: List[Dict]) -> str:
    
    try:
        logger.debug("일반 텍스트 후처리 시작")

        lines = []
        current_line = []

        for block in blocks:  # 이미 정렬된 상태
            text = block.get("text", "").strip()
            if not text:
                continue

            current_line.append(text)

            if block.get("lineBreak", False):
                lines.append(" ".join(current_line))
                current_line = []

        if current_line:
            lines.append(" ".join(current_line))
            
        logger.debug("텍스트 후처리 완료")

        return "\n".join(lines)
    except Exception as e:
        logger.error("일반 텍스트 후처리 중 오류 발생", exc_info=True)
        return "후처리 실패"