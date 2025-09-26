from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

#1. ocr로 추출된 json에서 필요한 정보(bounding box, text, linebreak)만 추출
def extract_blocks_from_ocr_response(ocr_response: Dict) -> List[Dict]:
    
    blocks = []
    
    try:
            image_info = ocr_response["images"][0]
            image_fields = image_info["fields"]
            image_width = image_info["convertedImageInfo"]["width"]
            image_height = image_info["convertedImageInfo"]["height"]
    except (KeyError, IndexError, TypeError) as e:
        logger.debug(f"OCR 응답에서 이미지 정보 추출 실패: {e}")
        raise

    for idx, field in enumerate(image_fields):
        try:
            vertices = field["boundingPoly"]["vertices"]
            x = min(v["x"] for v in vertices)
            y = min(v["y"] for v in vertices)
            w = max(v["x"] for v in vertices) - x
            h = max(v["y"] for v in vertices) - y

            block = {
                "x": x,
                "y": y,
                "w": w,
                "h": h,
                "text": field["inferText"],
                "linebreak": field["lineBreak"],
                "image_width": image_width,
                "image_height": image_height
            }

            blocks.append(block)

        except KeyError as e:
            logger.debug(f"필드 누락 (index {idx}): {e}")
            continue
        except Exception as e:
            logger.debug(f"블록 처리 중 예외 발생 (index {idx})", exc_info=True)
            continue

    return blocks