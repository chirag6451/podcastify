from celery import Celery
from celery_app.worker_config import (
    task_queues,
    task_routes,
    optimize_settings
)

# Initialize Celery app
celery_app = Celery('podcraftai',
                    broker='redis://localhost:6379/0',
                    backend='redis://localhost:6379/0')

# Configure Celery with optimized settings
celery_app.conf.update(
    task_queues=task_queues,
    task_routes=task_routes,
    **optimize_settings
)

# Include tasks
celery_app.autodiscover_tasks(['celery_app'], force=True)

if __name__ == '__main__':
    celery_app.start()
