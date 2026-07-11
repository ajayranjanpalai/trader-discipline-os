from datetime import datetime

from . import db


class AIInsight(db.Model):
    __tablename__ = "ai_insights"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    insight_type = db.Column(db.String(60), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    confidence = db.Column(db.Integer, default=75)
    severity = db.Column(db.String(20), default="info")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "insight_type": self.insight_type,
            "title": self.title,
            "message": self.message,
            "confidence": self.confidence,
            "severity": self.severity,
            "created_at": self.created_at.isoformat(),
        }
