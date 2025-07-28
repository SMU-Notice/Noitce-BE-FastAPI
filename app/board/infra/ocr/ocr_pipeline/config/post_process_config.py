from .section_classification_config import section_classification_config

#섹션별 후처리 config
post_process_config = {
    "table": {
        "max_iterations" : 3
        
    },
    "column": {
        "text_join_Delim": " "
    },
    "timeline": {
        "min_pair": 3,
        "y_tolerance" : 20
    }
}

classifier_config = section_classification_config