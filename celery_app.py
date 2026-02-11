from celery import Celery
from celery.schedules import crontab

celery_app = Celery(
    "hillel_pro",
    broker="amqp://guest:guest@rabbitmq:5672//",
    backend="rpc://",
)

celery_app.conf.timezone = "UTC"

celery_app.conf.beat_schedule = {
    "send-daily-new-films": {
        "task": "tasks.send_daily_new_films",
        "schedule": crontab(hour=9, minute=0),
    },
}

import tasks