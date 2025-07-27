import requests
import base64
import json
import uuid
import time
from typing import List, Dict
import logging

from .config.env import CLOVA_OCR_URL, CLOVA_SECRET_KEY 


logger = logging.getLogger(__name__)

def call_clova_ocr (image_path : str) -> Dict:
    logger.info(f"OCR 요청 시작: {image_path}")
    
    try:
        with open(image_path, "rb") as f:
            image_data = f.read()
        logger.debug("이미지 파일 읽기 완료")
        
        #CLOVA OCR은 base64로 인코딩된 이미지 문자열을 받음
        #이미지 -> 바이트 문자 -> 문자열 
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        logger.debug("이미지 base64 인코딩 완료")
        
        payload = {
            "images": [
                {
                    "format": image_path.split('.')[-1],
                    "name": "ocr_test",
                    "data": image_base64
                }
            ],
            "requestId": str(uuid.uuid4()),
            "version": "V2",
            "timestamp" : int(time.time() * 1000)
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-OCR-SECRET": CLOVA_SECRET_KEY
        }
        
        response = requests.post(CLOVA_OCR_URL, headers= headers, data = json.dumps(payload))
        response.raise_for_status()
        result = response.json()
        
        logger.info("OCR 요청 성공")
        return result
    
    except requests.RequestException as e:
        logger.error("OCR 요청 실패", exc_info=True)
        raise

    except Exception as e:
        logger.exception("알 수 없는 오류 발생")
        raise