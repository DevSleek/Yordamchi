from celery import Celery
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")  # agar Django loyihasi bilan integratsiya bo'lsa
app = Celery("bot")
app.config_from_object("django.conf:settings", namespace="CELERY")  # Django bo'lmasa, bu qatorni o'chirish mumkin
app.autodiscover_tasks(["bot"])


from celery.schedules import crontab

app.conf.beat_schedule = {
    "pre-message": {
        "task": "bot.tasks.send_pre_message",
        "schedule": crontab(hour=11, minute=55),
    },
    "daily-message": {
        "task": "bot.tasks.send_daily_message",
        "schedule": crontab(hour=12, minute=0),
    },
    "delete-messages": {
        "task": "bot.tasks.delete_bot_messages",
        "schedule": crontab(hour=12, minute=30),
    },
}
