import os

def get_required_env(key: str) -> str:
    value = os.getenv(key)
    if value is None:
        raise ValueError(f"필수 환경변수 '{key}'가 설정되지 않았습니다.")
    return value