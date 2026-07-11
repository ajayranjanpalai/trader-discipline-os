from datetime import datetime

from models import Task, TaskEmailLog, User, db
from services.emailer import send_email


def today():
    return datetime.now().date()


def effective_completed(task, current_date=None):
    current_date = current_date or today()
    if (task.task_scope or "today") == "daily":
        return bool(task.completed_at and task.completed_at.date() == current_date)
    return bool(task.completed)


def task_warning_state(task, current_date=None):
    current_date = current_date or today()
    if effective_completed(task, current_date):
        return None
    scope = task.task_scope or "today"
    if scope in {"daily", "today"} or task.due_date == current_date:
        return "Complete by today"
    if task.due_date and task.due_date < current_date:
        return "Overdue"
    return None


def warning_tasks(user_id, current_date=None):
    current_date = current_date or today()
    return [
        task for task in Task.query.filter_by(user_id=user_id).all()
        if task_warning_state(task, current_date)
    ]


def build_task_warning_body(user, tasks, current_date=None):
    current_date = current_date or today()
    lines = [
        f"Hi {user.name},",
        "",
        f"It is 12:00 PM on {current_date.isoformat()}. These Trader Discipline OS tasks need attention:",
        "",
    ]
    for task in tasks:
        due = task.due_date.isoformat() if task.due_date else "today"
        lines.append(f"- {task.title} [{task.category}] - {task_warning_state(task, current_date)} - due {due}")
    lines.extend(["", "Open Trader Discipline OS and complete the tasks that are due."])
    return "\n".join(lines)


def send_user_task_warning_email(user, current_date=None, notification_type="manual_task_warning", mark_sent=False):
    current_date = current_date or today()
    tasks = warning_tasks(user.id, current_date)
    if not tasks:
        return False, "No task warnings to email.", 0

    sent, message = send_email(
        user.email,
        f"Task warning - {len(tasks)} task{'s' if len(tasks) != 1 else ''} need attention",
        build_task_warning_body(user, tasks, current_date),
    )
    if sent and mark_sent:
        db.session.add(TaskEmailLog(
            user_id=user.id,
            sent_for_date=current_date,
            notification_type=notification_type,
        ))
        db.session.commit()
    return sent, message, len(tasks)


def already_sent_noon_warning(user_id, current_date=None):
    current_date = current_date or today()
    return bool(TaskEmailLog.query.filter_by(
        user_id=user_id,
        sent_for_date=current_date,
        notification_type="noon_task_warning",
    ).first())


def send_due_task_warnings_for_all_users(current_date=None):
    current_date = current_date or today()
    sent_count = 0
    skipped_count = 0
    failed = []
    for user in User.query.all():
        if already_sent_noon_warning(user.id, current_date):
            skipped_count += 1
            continue
        if not warning_tasks(user.id, current_date):
            skipped_count += 1
            continue
        sent, message, _count = send_user_task_warning_email(
            user,
            current_date=current_date,
            notification_type="noon_task_warning",
            mark_sent=True,
        )
        if sent:
            sent_count += 1
        else:
            failed.append({"email": user.email, "error": message})
    return {"sent": sent_count, "skipped": skipped_count, "failed": failed}
