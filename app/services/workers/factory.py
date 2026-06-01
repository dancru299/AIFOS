from app.core.config import Settings
from app.models import TaskScope
from app.services.workers.base import BaseWorker
from app.services.workers.content import ContentWorker
from app.services.workers.scraping import ScrapingWorker
from app.services.workers.web import WebWorker


def get_worker_for_scope(task_scope: TaskScope, settings: Settings) -> BaseWorker:
    if task_scope == TaskScope.WRITING:
        return ContentWorker(settings)
    if task_scope == TaskScope.SCRAPING:
        return ScrapingWorker(settings)
    return WebWorker(settings)
