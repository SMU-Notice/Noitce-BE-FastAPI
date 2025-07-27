import os
import json
import requests
import re
import glob
import uuid
from urllib.parse import urlparse
from tempfile import NamedTemporaryFile
from .ocr_pipeline.clova_ocr import call_clova_ocr
from .ocr_pipeline.config.env import WORKSPACE_DIR 

# OCR 결과 저장 경로
os.makedirs(WORKSPACE_DIR, exist_ok=True)

#ocr 결과로 나오는 json 파일명을 무작위로 설정
def sanitize_filename(s: str, count: int, max_length: int = 40) -> str:
    """
    OCR 결과 파일명을 안전하고 고유하게 생성
    - count: OCR 실행 순서 (1부터 증가)
    - s: 원본 이름 (예: 이미지 URL 또는 제목 일부)
    """

    # 랜덤 접두사 (앞쪽에 배치)
    rand_prefix = uuid.uuid4().hex[:5]

    # 알파벳/숫자만 남기고 나머지는 _로 대체
    safe = re.sub(r"[^a-zA-Z0-9]", "_", s)

    # 최대 길이 내로 자르기 (count + rand_prefix 포함)
    remaining = max_length - len(str(count)) - len(rand_prefix) - 2  # "_" 2개
    safe = safe[:remaining].rstrip("_")

    # 최종 파일명: "3_ab12c_notice_title"
    return f"{count}_{rand_prefix}_{safe}"

def get_next_ocr_count(workspace_dir: str) -> int:
    """
    해당 디렉토리 내 OCR 결과 파일 개수를 기준으로 다음 번호(count) 반환
    """
    existing_jsons = glob.glob(os.path.join(workspace_dir, "*.json"))
    return len(existing_jsons) + 1

def save_response_to_workspace(image_source: str):
    count = get_next_ocr_count(WORKSPACE_DIR)

    if image_source.startswith("http://") or image_source.startswith("https://"):
        response = requests.get(image_source)
        if response.status_code != 200:
            raise RuntimeError(f"이미지 다운로드 실패: {image_source}")

        parsed = urlparse(image_source)
        raw_query = parsed.query.strip()
        name_base = sanitize_filename(raw_query, count=count) or "image"

        with NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
            tmp_file.write(response.content)
            tmp_file_path = tmp_file.name
            print(f"이미지 다운로드 완료: {tmp_file_path}")

        image_path = tmp_file_path
        json_filename = f"{name_base}.json"

    else:
        base_name = os.path.basename(image_source)
        name_base = os.path.splitext(base_name)[0]
        name_base = sanitize_filename(name_base, count=count)
        json_filename = f"{name_base}.json"
        image_path = image_source

    output_path = os.path.join(WORKSPACE_DIR, json_filename)

    ocr_response = call_clova_ocr(image_path)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(ocr_response, f, ensure_ascii=False, indent=2)

    print(f"OCR 응답이 저장되었습니다:\n {output_path}")

    if image_source.startswith("http"):
        os.remove(image_path)


if __name__ == "__main__":
    save_response_to_workspace("https://www.smu.ac.kr/cms/plugin/editorImage.do?EwBmFYHoQdkgXAUgDQB4HsAqmCyAbAUQGsBTAGQAcAjHfAZwCEA6AKwoHMg")
