import threading
import time
from datetime import datetime

from services.task_notifications import send_due_task_warnings_for_all_users


def start_noon_task_email_scheduler(app):
    if getattr(app, "_task_email_scheduler_started", False):
        return
    app._task_email_scheduler_started = True

    def worker():
        while True:
            now = datetime.now()
            if now.hour == 12 and now.minute == 0:
                with app.app_context():
                    if app.config.get("MAIL_SERVER") and app.config.get("MAIL_DEFAULT_SENDER"):
                        send_due_task_warnings_for_all_users(now.date())
                time.sleep(70)
            else:
                time.sleep(20)

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
