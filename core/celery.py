import platform
from celery import Celery
from celery.schedules import crontab
from core.config import celery_settings, db_settings 

app = Celery("reeloid_fastapi")

# Redis as the broker, MongoDB for storing results
app.conf.broker_url = celery_settings.CELERY_BROKER_URL
app.conf.result_backend = db_settings.MONGODB_URI + "/celery_results"

# app.autodiscover_tasks('streaming_app_backend')
app.autodiscover_tasks(["payments", "users", "sliders"])

app.conf.beat_schedule = {
    "run_daily_auto_check": {
        "task": "helper_function.autoCheckInPointAllotement.autoCheckInPointAllotement",
        "schedule": crontab(minute=0, hour=0),
    },
}


# Choose correct pool automatically
CELERY_WORKER_POOL = "solo" if platform.system() == "Windows" else "prefork"


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
