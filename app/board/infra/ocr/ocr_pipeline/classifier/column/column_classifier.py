import numpy as np
from typing import List, Dict
from .cluster_blocks import cluster_blocks_by_x
import logging

logger = logging.getLogger(__name__)

def score_column_section(
    section: List[Dict],
    min_columns: int,
    min_blocks_per_column: int,
    min_threshold: int,
    max_threshold: int,
    multiplier: float
) -> float:
    """
    컬럼 섹션일 확률을 0~1 사이 점수로 반환
    """
    try:
        if len(section) < min_columns * min_blocks_per_column:
            logger.debug(f"[column] 블록 수 부족: {len(section)}")
            return 0.0

        x_centers = [block["x"] + block["w"] // 2 for block in section]

        # 동적 클러스터 임계값 계산
        avg_block_width = np.mean([b["w"] for b in section])
        std_block_width = np.std([b["w"] for b in section])
        estimated_gap = avg_block_width + std_block_width
        
        # std가 크면 multiplier 보정
        if std_block_width > 60:
            multiplier += 0.1  

        x_cluster_threshold = int(np.clip(estimated_gap * multiplier, min_threshold, max_threshold))
        x_std_threshold = int(np.clip(std_block_width * 2.0, 30, 140))

        x_centers_sorted = sorted(x_centers)
        
        # 실제 클러스터링 실행
        clusters = cluster_blocks_by_x(section, x_cluster_threshold)
        num_columns = len(clusters)
        block_per_column = [len(col) for col in clusters]
        std_column_size = np.std(block_per_column) if len(block_per_column) >= 2 else 999

        x_centers = [block["x"] + block["w"] // 2 for block in section]
        x_std = np.std(x_centers)

        # --- 점수 계산 ---
        # 1. 컬럼 수 기준
        if num_columns < min_columns:
            column_count_score = 0.0
        elif min_columns <= num_columns <= 2:
            column_count_score = 0.7
        elif num_columns == 3:
            column_count_score = 0.5
        elif num_columns == 4:
            column_count_score = 0.3
        else:
            column_count_score = 0.0

        # 2. 컬럼 블록 수 균형
        if std_column_size < len(section) * 0.2:
            column_balance_score = 1.0
        elif std_column_size < len(section) * 0.3:
            column_balance_score = 0.5
        else:
            column_balance_score = 0.0

        # 3. x 좌표 분포 (너무 퍼지면 감점)
        if x_std < x_std_threshold:
            x_std_score = 1.0
        elif x_std < x_std_threshold * 1.5:
            x_std_score = 0.5
        else:
            x_std_score = 0.0

        # 최종 점수 계산
        final_score = round((
            column_count_score * 0.4 +
            column_balance_score * 0.3 +
            x_std_score * 0.3
        ), 2)
        
        # 컬럼 신뢰도 보정: 컬럼 수 적고 좌표 분산이 큰 경우 감점
        if num_columns <= 3 and x_std > 180:
            logger.debug(f"[column] 컬럼 수({num_columns}) 적고 x_std({x_std:.2f}) 큼 → column score 감점")
            final_score = round(final_score * 0.7, 2)
        
        # 컬럼 수가 1인 경우
        if num_columns == 1:
            if x_std > 200:
                logger.debug("[column] 컬럼 수는 1이지만 x_std 큼 → 판단 유예")
                final_score = max(final_score, 0.25)
            else:
                logger.debug("[column] 컬럼 수가 1 → 컬럼으로 간주하지 않음")
                final_score = min(final_score, 0.10)
        # 컬럼 수 2~3인데 분산 크고 블록 충분하면 부분 보정
        elif 2 <= num_columns <= 3 and x_std > 220 and len(section) >= 16:
            logger.debug("[column] 컬럼 수 적고 x_std 크지만 블록 충분 → 보정")
            final_score = max(final_score, 0.40)

        logger.debug(
            f"[column] 컬럼수: {num_columns}, 분포 std: {std_column_size:.2f}, "
            f"x std: {x_std:.2f}, 최종 점수: {final_score:.2f}"
        )
        return final_score

    except Exception as e:
        logger.exception("[column] 컬럼 판별 중 예외 발생")
        return 0.0
