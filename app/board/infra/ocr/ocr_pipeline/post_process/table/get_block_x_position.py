from typing import Dict

def get_block_x_position(block:Dict, alignment:str) -> int:
    if alignment == "left":
        return block["x"]
    elif alignment == "center":
        return block["x"] + block["w"] // 2
    elif alignment == "right":
        return block["x"] + block["w"]
    else:
        return block["x"] + block["w"] // 2