from .ocr_pipeline.call_clova import call_clova_ocr
from .ocr_pipeline.post_process_pipeline import post_process_pipeline
from .ocr_pipeline.config import section_classification_config, post_process_config
from app.board.application.ports.ocr_port import OCRPort
import logging
from typing import List


logger = logging.getLogger(__name__)


class ClovaOCRAdapter(OCRPort):
      
   def extract_text_from_image_pipeline(self, image_path: str) -> str:
        ocr_response = call_clova_ocr(image_path)

        results: List[str] = post_process_pipeline(
            ocr_response, 
            section_classification_config.section_classification_config, 
            post_process_config.post_process_config
        )
        # 후처리 결과를 로그로 출력
        logger.info("최종 결과:")
        for idx, section in enumerate(results):
            logger.info(f"\n--- Section {idx + 1} ---\n{section}")

        # 구분자로 연결해서 문자열로 반환
        return "\n\n---\n\n".join(results)


# if __name__ == "__main__":
#     import sys
#     if len(sys.argv) < 2:
#         print("이미지 경로를 인자로 입력하세요: python main.py image.jpg")
#         sys.exit(1)

#     image_path = sys.argv[1]
#     final_result = run_ocr_pipeline(image_path)

#     print("\n 최종 결과:")
#     for idx, section in enumerate(final_result):
#         print(f"\n--- Section {idx + 1} ---")
#         print(section)