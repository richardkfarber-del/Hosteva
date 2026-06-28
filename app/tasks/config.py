from celery import Celery
import os

REDIS_URL = os.getenv("REDIS_URL") or "redis://localhost:6379/0"

celery_app = Celery(
    "hosteva",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.tasks.audit", "app.tasks.calendar", "app.tasks.inbox", "app.tasks.scraper"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Enable eager execution in testing
if os.getenv("ENVIRONMENT") == "testing" or os.getenv("DATABASE_URL", "").startswith("sqlite:///./test"):
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True
