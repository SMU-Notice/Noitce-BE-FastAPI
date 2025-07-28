from typing import List, Dict
import numpy as np

#테이블의 열 별로 정렬 방식 판단
def infer_alignment(blocks: List[Dict],
                    std_threshold: int
                    ) -> str:
    if not blocks:
        return "unknown"
    
    # 정렬 방식 판단에 필요한 데이터
    lefts = [block["x"] for block in blocks]
    centers = [block["x"] + block["w"]// 2 for block in blocks]
    rights =  [block["x"] + block["w"] for block in blocks]
    
    stds = {
        "left" : float(np.std(lefts)),
        "center" : float(np.std(centers)),
        "right" : float(np.std(rights))
    }
    
    #세 방식 중 표준편차가 가장 작은 항목
    min_align = min(stds, key=lambda k: stds[k])
    #의 실제 표준편차값
    min_std = stds[min_align]
    
    
    sorted_stds = sorted(stds.items(), key = lambda x: x[1])
    
    # 블록 수가 적으면 분산이 적게 나올 수밖에 없음
    # 더 확실한 정렬 방식 판단을 위함
    if len(blocks) < 3:
        if sorted_stds[0][1] - sorted_stds[1][1] > std_threshold:
            return sorted_stds[0][0]
        else:
            return "unknown"
    else:
        return min_align