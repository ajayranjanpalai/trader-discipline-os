from datetime import datetime, timedelta
from random import SystemRandom
from secrets import token_urlsafe

from werkzeug.security import generate_password_hash

from . import db


_random = SystemRandom()


class PendingSignup(db.Model):
    __tablename__ = "pending_signups"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    verification_code = db.Column(db.String(12), nullable=False)
    confirm_token = db.Column(db.String(160), unique=True, nullable=False, index=True)
    decline_token = db.Column(db.String(160), unique=True, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    def create(cls, name, email, password):
        return cls(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            verification_code=f"{_random.randrange(100000, 1000000)}",
            confirm_token=token_urlsafe(32),
            decline_token=token_urlsafe(32),
            expires_at=datetime.utcnow() + timedelta(minutes=15),
        )

    @property
    def expired(self):
        return datetime.utcnow() > self.expires_at
