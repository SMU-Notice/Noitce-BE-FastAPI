from typing import List, Dict
import logging
import numpy as np

logger = logging.getLogger(__name__)

def is_simple_column(blocks: List[Dict]) -> bool:
    if len(blocks) < 2:
        return True  # 블록이 1개 이하라면 복잡성 판단 의미 없으므로 단순 컬럼으로 간주

    # 각 블록의 x 좌표 리스트 (세로 정렬 정도를 판단하기 위함)
    x_positions = [b["x"] for b in blocks if "x" in b]

    # 각 블록의 y 중심값 리스트 (y + h/2)
    y_centers = [b["y"] + b.get("h", 0) // 2 for b in blocks]

    # 블록들의 높이 리스트 (0 초과인 경우만)
    heights = [b.get("h", 0) for b in blocks if b.get("h", 0) > 0]

    # 블록 평균 높이 계산 (이 값 기반으로 기준 임계값을 정함)
    avg_height = np.mean(heights) if heights else 20  # heights 비어있으면 기본값 20 사용

    # x 좌표 표준편차 → 블록이 좌우로 얼마나 퍼져있는지 판단 (낮을수록 단일 컬럼일 가능성 높음)
    x_std = np.std(x_positions)

    # y 중심값들의 간격 리스트 계산
    y_diffs = [j - i for i, j in zip(y_centers[:-1], y_centers[1:])]

    # y 간격의 표준편차 → 줄 간 간격이 얼마나 일정한지 판단
    y_gap_std = np.std(y_diffs) if y_diffs else 0

    # x, y 판단 기준 임계값 설정 (평균 높이에 비례한 상대 기준)
    x_std_threshold = avg_height * 1.8      # x 좌표 표준편차가 이보다 작으면 좌우 정렬로 간주
    y_std_threshold = avg_height * 1.5      # y 간격 표준편차가 이보다 작으면 줄 간 간격이 일정하다고 간주

    # 디버깅 로그 출력
    logger.debug(f"[is_simple_column] x_std: {x_std:.1f}, y_gap_std: {y_gap_std:.1f}, 기준(x:{x_std_threshold:.1f}, y:{y_std_threshold:.1f})")

    # 두 기준을 모두 만족하면 단순 텍스트 컬럼으로 판단
    return bool(x_std < x_std_threshold and y_gap_std < y_std_threshold)
