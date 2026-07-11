from datetime import date, datetime

from . import db


class TaskEmailLog(db.Model):
    __tablename__ = "task_email_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    sent_for_date = db.Column(db.Date, nullable=False, default=date.today)
    notification_type = db.Column(db.String(40), nullable=False, default="noon_task_warning")
    sent_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("user_id", "sent_for_date", "notification_type", name="uq_task_email_once_per_day"),
    )
