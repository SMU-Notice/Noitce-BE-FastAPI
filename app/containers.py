from dependency_injector import containers, providers
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
from app.board.infra.http_new_post_sender import HttpNewPostSender
from app.board.application.post_classifier import PostClassifier
from app.board.application.ports.new_post_sender import INewPostSender
from app.board.application.scraped_post_manager import ScrapedPostManager
from app.board.infra.scraper.posts.scraper_factory import PostScraperFactory

from app.protest.application.protest_event_service import ProtestEventService
from app.protest.domain.repository.protest_event_repo import IProtestEventRepository
from app.protest.infra.repository.protest_event_repo import ProtestEventRepository  # 실제 구현체

class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=["."],  # 모든 패키지에서 사용 가능
    )
    
    # 스케줄러와 락
    scheduler = providers.Singleton(AsyncIOScheduler)
    scrape_lock = providers.Singleton(asyncio.Lock)

    # sender와 classifier
    post_classifier = providers.Singleton(PostClassifier)
    http_new_post_sender = providers.Singleton(HttpNewPostSender)
    new_post_sender = providers.AbstractSingleton(INewPostSender)
    
    # ScrapedPostManager (의존성 주입)
    scraped_post_manager = providers.Singleton(
        ScrapedPostManager,
        new_post_sender=new_post_sender
    )

    post_scraper_factory = providers.Singleton(PostScraperFactory)
    
    protest_event_repository = providers.Singleton(ProtestEventRepository)  # AbstractSingleton 대신
    
    protest_service = providers.Singleton(
        ProtestEventService,
        protest_event_repository=protest_event_repository
    )