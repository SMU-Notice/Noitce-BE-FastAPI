import requests
import base64
import os
import json
import uuid
import time
from typing import List, Dict
from tempfile import NamedTemporaryFile
import logging

from .config.env import CLOVA_OCR_URL, CLOVA_SECRET_KEY 

logger = logging.getLogger(__name__)

def call_clova_ocr(image_source: str) -> Dict:
    """
    이미지 파일 경로 또는 URL을 받아 CLOVA OCR 요청 수행
    """
    logger.info(f"OCR 요청 시작: {image_source}")

    temp_file = None

    try:
        # 1. 이미지가 URL인 경우 다운로드해서 메모리 임시파일로 저장
        if image_source.startswith("http://") or image_source.startswith("https://"):
            response = requests.get(image_source)
            response.raise_for_status()
            temp_file = NamedTemporaryFile(delete=False, suffix=".jpg")
            temp_file.write(response.content)
            temp_file.flush()
            image_path = temp_file.name
            logger.debug(f"이미지 URL 다운로드 및 임시 저장 완료: {image_path}")
        else:
            image_path = image_source

        # 2. 이미지 파일 읽기
        with open(image_path, "rb") as f:
            image_data = f.read()
        logger.debug("이미지 파일 읽기 완료")

        # 3. Base64 인코딩
        image_base64 = base64.b64encode(image_data).decode("utf-8")
        logger.debug("이미지 base64 인코딩 완료")

        # 4. CLOVA OCR API 요청
        payload = {
            "images": [{
                "format": image_path.split('.')[-1],
                "name": "ocr_test",
                "data": image_base64
            }],
            "requestId": str(uuid.uuid4()),
            "version": "V2",
            "timestamp": int(time.time() * 1000)
        }

        headers = {
            "Content-Type": "application/json",
            "X-OCR-SECRET": CLOVA_SECRET_KEY
        }

        response = requests.post(CLOVA_OCR_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        result = response.json()

        logger.info("OCR 요청 성공")
        return result

    except requests.RequestException:
        logger.error("OCR 요청 실패", exc_info=True)
        raise

    except Exception:
        logger.exception("알 수 없는 오류 발생")
        raise

    finally:
        # URL에서 다운로드한 임시 파일 삭제
        if temp_file is not None:
            temp_file.close()
            if os.path.exists(temp_file.name):
                os.remove(temp_file.name)
                logger.debug(f"임시 이미지 파일 삭제 완료: {temp_file.name}")
