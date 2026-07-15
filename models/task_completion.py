from datetime import date, datetime

from . import db


class TaskCompletion(db.Model):
    __tablename__ = "task_completions"
    __table_args__ = (
        db.UniqueConstraint("task_id", "completed_on", name="uq_task_completion_once_per_day"),
    )

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False, index=True)
    completed_on = db.Column(db.Date, nullable=False, default=date.today, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
