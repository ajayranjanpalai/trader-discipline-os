from datetime import datetime, timedelta

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from models import Task, User, db
from services.emailer import email_configured
from services.task_notifications import effective_completed, send_user_task_warning_email, task_warning_state

tasks_bp = Blueprint("tasks", __name__)


def _today():
    return datetime.now().date()


def _parse_due_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def _effective_completed(task):
    return effective_completed(task, _today())


def _task_warning_state(task):
    return task_warning_state(task, _today())


def _stats(user_id):
    tasks = Task.query.filter_by(user_id=user_id).all()
    completed = [task for task in tasks if _effective_completed(task)]
    days = {task.completed_at.date() for task in completed if task.completed_at}
    today = _today()
    due_today = [task for task in tasks if _task_warning_state(task) == "Complete by today"]
    streak = 0
    cursor = today
    while cursor in days:
        streak += 1
        cursor -= timedelta(days=1)
    return {
        "total": len(tasks),
        "completed": len(completed),
        "completion_rate": round((len(completed) / len(tasks)) * 100, 1) if tasks else 0,
        "streak": streak,
        "due_today": len(due_today),
        "email_configured": email_configured(),
    }


@tasks_bp.get("")
@jwt_required()
def list_tasks():
    user_id = int(get_jwt_identity())
    tasks = Task.query.filter_by(user_id=user_id).order_by(Task.created_at.desc()).all()
    return {"tasks": [task.to_dict() for task in tasks], "stats": _stats(user_id)}


@tasks_bp.post("/warnings/email")
@jwt_required()
def email_task_warnings():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    sent, message, count = send_user_task_warning_email(user, current_date=_today())
    if not count:
        return {"message": message, "count": 0}
    if not email_configured():
        return {
            "message": "Email is not configured, so no warning email was sent.",
            "count": count,
            "email_configured": False,
        }
    if not sent:
        return {"error": message}, 503
    return {"message": message, "sent_to": user.email, "count": count}


@tasks_bp.post("")
@jwt_required()
def add_task():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    if not title:
        return {"error": "Task title is required."}, 400
    task_scope = data.get("task_scope") if data.get("task_scope") in {"daily", "today", "date"} else "today"
    due_date = _parse_due_date(data.get("due_date"))
    if task_scope == "date" and not due_date:
        return {"error": "Choose a due date for this task."}, 400
    if task_scope == "today":
        due_date = _today()
    if task_scope == "daily":
        due_date = None
    task = Task(
        user_id=int(get_jwt_identity()),
        title=title,
        category=data.get("category", "routine"),
        task_scope=task_scope,
        due_date=due_date,
    )
    db.session.add(task)
    db.session.commit()
    return {"task": task.to_dict(), "stats": _stats(task.user_id)}, 201


@tasks_bp.patch("/<int:task_id>/complete")
@jwt_required()
def complete_task(task_id):
    user_id = int(get_jwt_identity())
    task = Task.query.filter_by(id=task_id, user_id=user_id).first_or_404()
    if _effective_completed(task):
        task.completed = False
        task.completed_at = None
    else:
        task.completed = True
        task.completed_at = datetime.now()
    db.session.commit()
    return {"task": task.to_dict(), "stats": _stats(user_id)}


@tasks_bp.delete("/<int:task_id>")
@jwt_required()
def delete_task(task_id):
    user_id = int(get_jwt_identity())
    task = Task.query.filter_by(id=task_id, user_id=user_id).first_or_404()
    db.session.delete(task)
    db.session.commit()
    return {"message": "Task deleted.", "stats": _stats(user_id)}
