import os
from dotenv import load_dotenv
from .env_util import get_required_env

# .env 파일 로드
load_dotenv()

# CLOVA API 관련
CLOVA_OCR_URL = get_required_env("CLOVA_OCR_URL")
CLOVA_SECRET_KEY = get_required_env("CLOVA_SECRET_KEY")

#OCR 결과 json 파일 저장
WORKSPACE_DIR = os.getenv("WORKSPACE_DIR", os.path.join("C:", os.sep, "OCR_PIPELINE", "jsons"))

# 로깅 관련
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = os.getenv("LOG_FORMAT", "[%(asctime)s] %(levelname)s [%(name)s] - %(message)s")
LOG_DATE_FORMAT = os.getenv("LOG_DATE_FORMAT", "%Y-%m-%d %H:%M:%S")