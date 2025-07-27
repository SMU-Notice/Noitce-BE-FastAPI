#섹션 타입 판별 config
section_classification_config = {
    "table": {
        "overlap_ratio_threshold": 0.3,
        "min_rows" : 3,
        "colspan_check_enabled" : True
    },
    "column": {
        "min_columns" :  2,
        "min_blocks_per_column" : 8,
        "min_threshold" : 30,
        "max_threshold" : 120,
        "multiplier": 2.0
    },
    "timeline": {
        "min_pairs": 3
    }
}