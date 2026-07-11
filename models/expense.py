from datetime import datetime

from . import db


class Expense(db.Model):
    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    title = db.Column(db.String(140), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(40), nullable=False)
    payment_method = db.Column(db.String(40), nullable=False)
    note = db.Column(db.String(255), default="")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "amount": self.amount,
            "category": self.category,
            "payment_method": self.payment_method,
            "note": self.note,
            "timestamp": self.timestamp.isoformat(),
        }
