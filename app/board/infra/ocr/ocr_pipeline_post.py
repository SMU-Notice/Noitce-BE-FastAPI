import sys
import json
import logging

from .ocr_pipeline.post_process_pipeline import post_process_pipeline
from .ocr_pipeline.config import section_classification_config, post_process_config

logger = logging.getLogger(__name__)

def run_pipeline_from_saved_response(json_path: str) -> list:
    with open(json_path, "r", encoding="utf-8") as f:
        ocr_response = json.load(f)

    results = post_process_pipeline(
        ocr_response,
        section_classification_config.section_classification_config,
        post_process_config.post_process_config
    )

    logger.info("최종 결과:")
    for idx, section in enumerate(results):
        logger.info(f"\n--- Section {idx + 1} ---\n{section}")

    return results

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("사용법: python run_pipeline_with_saved_json.py <ocr_json_file>")
        sys.exit(1)

    json_path = sys.argv[1]
    run_pipeline_from_saved_response(json_path)