from datetime import datetime

from . import db


class Trade(db.Model):
    __tablename__ = "trades"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    pair = db.Column(db.String(40), nullable=False)
    direction = db.Column(db.String(10), nullable=False)
    entry = db.Column(db.Float, nullable=False)
    exit = db.Column(db.Float, nullable=False)
    remaining_exit = db.Column(db.Float, nullable=True, default=0.0)
    stop_loss = db.Column(db.Float, nullable=False)
    position_size = db.Column(db.Float, nullable=False)
    closed_quantity = db.Column(db.Float, default=0.0)
    remaining_quantity = db.Column(db.Float, default=0.0)
    pnl = db.Column(db.Float, nullable=False)
    brokerage = db.Column(db.Float, default=0.0)
    risk_reward = db.Column(db.Float, nullable=False)
    emotion = db.Column(db.String(40), nullable=False)
    trade_reason = db.Column(db.String(255), default="")
    notes = db.Column(db.Text, default="")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "pair": self.pair,
            "direction": self.direction,
            "entry": self.entry,
            "exit": self.exit,
            "remaining_exit": self.remaining_exit,
            "stop_loss": self.stop_loss,
            "position_size": self.position_size,
            "closed_quantity": self.closed_quantity or 0,
            "remaining_quantity": self.remaining_quantity or 0,
            "pnl": self.pnl,
            "brokerage": self.brokerage or 0,
            "risk_reward": self.risk_reward,
            "emotion": self.emotion,
            "trade_reason": self.trade_reason,
            "notes": self.notes,
            "timestamp": self.timestamp.isoformat(),
            "created_at": self.created_at.isoformat(),
        }
