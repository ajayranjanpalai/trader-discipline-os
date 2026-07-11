from datetime import datetime

from . import db


class DisciplineLog(db.Model):
    __tablename__ = "discipline_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    event_type = db.Column(db.String(60), nullable=False)
    severity = db.Column(db.String(20), default="info")
    message = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "event_type": self.event_type,
            "severity": self.severity,
            "message": self.message,
            "created_at": self.created_at.isoformat(),
        }
