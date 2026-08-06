from datetime import datetime
from . import db


class TradeTimelineEvent(db.Model):
    __tablename__ = "trade_timeline_events"

    id = db.Column(db.Integer, primary_key=True)
    trade_id = db.Column(db.Integer, db.ForeignKey("trades.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    action = db.Column(db.String(100), nullable=False)  # e.g. "Trade Opened", "Stop Loss Modified", "TP1 Hit"
    notes = db.Column(db.String(255), default="")

    def to_dict(self):
        return {
            "id": self.id,
            "trade_id": self.trade_id,
            "timestamp": self.timestamp.isoformat(),
            "action": self.action,
            "notes": self.notes or "",
        }


class MarketReplayNote(db.Model):
    __tablename__ = "market_replay_notes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    date = db.Column(db.String(10), nullable=False)  # YYYY-MM-DD
    bias = db.Column(db.String(50), default="Neutral")  # Bullish, Bearish, Neutral
    key_levels = db.Column(db.Text, default="")
    lessons = db.Column(db.Text, default="")
    mistakes = db.Column(db.Text, default="")
    what_worked = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date,
            "bias": self.bias,
            "key_levels": self.key_levels or "",
            "lessons": self.lessons or "",
            "mistakes": self.mistakes or "",
            "what_worked": self.what_worked or "",
            "created_at": self.created_at.isoformat(),
        }


class WatchlistItem(db.Model):
    __tablename__ = "watchlist_items"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False)  # Crypto, Forex, Stocks, Indices, Commodities
    symbol = db.Column(db.String(40), nullable=False)
    notes = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "category": self.category,
            "symbol": self.symbol,
            "notes": self.notes or "",
            "created_at": self.created_at.isoformat(),
        }


class TradingSetup(db.Model):
    __tablename__ = "trading_setups"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)  # e.g., "EMA Pullback"
    version = db.Column(db.String(20), default="v1")  # e.g., "v1", "v2"
    category = db.Column(db.String(50), default="General")  # Scalping, Swing, Forex, etc.
    conditions_json = db.Column(db.Text, default="[]")  # List of checklist items
    is_favorite = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "category": self.category,
            "conditions_json": self.conditions_json or "[]",
            "is_favorite": bool(self.is_favorite),
            "notes": self.notes or "",
            "created_at": self.created_at.isoformat(),
        }


class TradingRule(db.Model):
    __tablename__ = "trading_rules"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    rule_text = db.Column(db.String(255), nullable=False)  # e.g. "Never risk above 2%"
    category = db.Column(db.String(50), default="Risk")  # Risk, Discipline, Execution
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "rule_text": self.rule_text,
            "category": self.category,
            "is_active": bool(self.is_active),
            "created_at": self.created_at.isoformat(),
        }


class DailyDiary(db.Model):
    __tablename__ = "daily_diaries"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    date = db.Column(db.String(10), nullable=False)  # YYYY-MM-DD
    todays_goal = db.Column(db.Text, default="")
    todays_mood = db.Column(db.String(50), default="Focused")
    todays_lesson = db.Column(db.Text, default="")
    tomorrows_focus = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date,
            "todays_goal": self.todays_goal or "",
            "todays_mood": self.todays_mood or "Focused",
            "todays_lesson": self.todays_lesson or "",
            "tomorrows_focus": self.tomorrows_focus or "",
            "created_at": self.created_at.isoformat(),
        }


class SessionNote(db.Model):
    __tablename__ = "session_notes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    date = db.Column(db.String(10), nullable=False)  # YYYY-MM-DD
    phase = db.Column(db.String(50), nullable=False)  # Pre-Market, Opening, Mid-Day, Closing, Post-Market
    content = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date,
            "phase": self.phase,
            "content": self.content or "",
            "created_at": self.created_at.isoformat(),
        }


class EconomicEvent(db.Model):
    __tablename__ = "economic_events"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    date = db.Column(db.String(10), nullable=False)
    event_name = db.Column(db.String(100), nullable=False)  # e.g., "FOMC Interest Rate", "NFP"
    market_reaction = db.Column(db.Text, default="")
    trade_taken = db.Column(db.String(100), default="")
    lesson_learned = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date,
            "event_name": self.event_name,
            "market_reaction": self.market_reaction or "",
            "trade_taken": self.trade_taken or "",
            "lesson_learned": self.lesson_learned or "",
            "created_at": self.created_at.isoformat(),
        }


class LearningResource(db.Model):
    __tablename__ = "learning_resources"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    resource_type = db.Column(db.String(50), default="Book")  # Book, Video, Article, PDF, Course
    link_or_notes = db.Column(db.Text, default="")
    status = db.Column(db.String(30), default="To Learn")  # To Learn, In Progress, Completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "resource_type": self.resource_type,
            "link_or_notes": self.link_or_notes or "",
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }


class TradingMilestone(db.Model):
    __tablename__ = "trading_milestones"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    title = db.Column(db.String(100), nullable=False)  # e.g., "First 100 Trades"
    description = db.Column(db.String(255), default="")
    target_value = db.Column(db.Float, default=0.0)
    current_value = db.Column(db.Float, default=0.0)
    is_unlocked = db.Column(db.Boolean, default=False)
    unlocked_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description or "",
            "target_value": self.target_value,
            "current_value": self.current_value,
            "is_unlocked": bool(self.is_unlocked),
            "unlocked_at": self.unlocked_at.isoformat() if self.unlocked_at else None,
        }
