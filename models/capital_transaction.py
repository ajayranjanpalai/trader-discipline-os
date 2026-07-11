from datetime import datetime

from . import db


class CapitalTransaction(db.Model):
    __tablename__ = "capital_transactions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    transaction_type = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    note = db.Column(db.String(255), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "transaction_type": self.transaction_type,
            "amount": self.amount,
            "note": self.note,
            "created_at": self.created_at.isoformat(),
        }
