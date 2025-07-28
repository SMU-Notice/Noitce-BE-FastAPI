from typing import List, Dict
from .get_block_x_position import get_block_x_position
from .infer_alignment import infer_alignment
import numpy as np
import logging

logger = logging.getLogger(__name__)

#블록들을 정렬 방식에 맞춰서 열 별로 배치
def align_blocks_to_columns(
    rows: List[List[Dict]],
    x_tolerance: int,
    std_threshold: int,
    max_iterations: int
) -> List[List[List[Dict]]]:
    
    #1) 전체 블록 수집
    all_blocks = [block for row in rows for block in row]


    #2) 초기의 정렬 기준 X 좌표는 center라고 가정
    for block in all_blocks:
        block["aligned_x"] = block["x"] + block["w"] // 2
        
    column_reps = []
    
    for iteration in range(max_iterations):
        #3) 열의 기준 X 좌표 클러스터링
        aligned_x_list = sorted(set(block["aligned_x"] for block in all_blocks))
        new_column_reps = []
        
        for x in aligned_x_list:
            placed = False
            for i, rep in enumerate(new_column_reps):
                if abs(rep - x) <= x_tolerance:
                    new_column_reps[i] = (rep + x) / 2
                    placed = True
                    break
            if not placed:
                new_column_reps.append(x)
        
        #각 열이 어떤 X 좌표 근처에 위치하는지 나타냄
        new_column_reps = sorted(new_column_reps)
        
        # 열 수 다르면 수렴 검사 skip
        if column_reps and len(column_reps) == len(new_column_reps):
            if np.allclose(column_reps, new_column_reps, atol=1e-2):
                logger.debug(f"[align] {iteration+1}회 반복 후 열 기준 수렴 완료")
                break
        
        column_reps = new_column_reps
        
        #4) 열별로 블록 분배
        col_blocks_map = {i: [] for i in range(len(column_reps))}
        for block in all_blocks:
            idx = np.argmin([abs(rep - block["aligned_x"]) for rep in column_reps])
            col_blocks_map[int(idx)].append(block)
            
        #5) 열별 정렬 기준 추론
        col_alignments = {
            i : infer_alignment(col_blocks_map[i], std_threshold)
            for i in col_blocks_map
        }
        
        #6) 정렬 기준에 따라 각 블록의 aligned_x 재계산
        for block in all_blocks:
            col_idx = np.argmin([abs(rep - block["aligned_x"]) for rep in column_reps]) 
            alignment = col_alignments.get(int(col_idx), "center")
            block["aligned_x"] = get_block_x_position(block, alignment)
    
    #4) 각 행 내의 블록들을 열 기준에 따라 할당
    max_cols = len(column_reps)
    table = []
    for row in rows:
        columns = [[] for _ in range(max_cols)]
        for block in row:
            block_x = block["aligned_x"]
            idx = np.argmin([abs(rep - block_x) for rep in column_reps])
            columns[idx].append(block)
        table.append(columns)
        
    return table
