# app/config/container_config.py
import os
from app.containers import Container

def configure_container() -> Container:
    """컨테이너 설정 및 의존성 바인딩"""
    container = Container()
    
    # 현재는 HTTP sender만 있으므로 바로 바인딩
    configure_senders(container)
    
    return container

def configure_senders(container: Container):
    """Sender 관련 바인딩"""
    container.new_post_sender.override(container.http_new_post_sender)