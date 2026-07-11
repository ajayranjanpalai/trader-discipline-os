from datetime import datetime, time

from models import DisciplineLog, Trade, db

DELTA_USD_INR_RATE = 85


def _net_pnl_inr(trade):
    return (float(trade.pnl or 0) * DELTA_USD_INR_RATE) - float(getattr(trade, "brokerage", 0) or 0)


def _day_window(reference_time=None):
    reference_time = reference_time or datetime.utcnow()
    start = datetime.combine(reference_time.date(), time.min)
    end = datetime.combine(reference_time.date(), time.max)
    return start, end


def day_trades(user_id, reference_time=None, exclude_trade_id=None):
    start, end = _day_window(reference_time)
    query = (
        Trade.query.filter(
            Trade.user_id == user_id,
            Trade.timestamp >= start,
            Trade.timestamp <= end,
        )
    )
    if exclude_trade_id is not None:
        query = query.filter(Trade.id != exclude_trade_id)
    return query.order_by(Trade.timestamp.asc()).all()


def today_trades(user_id):
    return day_trades(user_id)


def _rule_status(trades):
    losses = [trade for trade in trades if _net_pnl_inr(trade) < 0]

    if len(losses) >= 2:
        return False, "TWO_LOSSES_LOCK", "Two losses recorded today. Trading is blocked."

    if len(trades) >= 2:
        return False, "DAILY_LIMIT", "Max 2 trades reached. Trading is blocked for today."

    return True, "CLEAR", "Discipline engine cleared this trade."


def evaluate_trade_permission(user_id, reference_time=None):
    return _rule_status(day_trades(user_id, reference_time))


def validate_trade_day(user_id, trade_fields, exclude_trade_id=None):
    trades = day_trades(user_id, trade_fields["timestamp"], exclude_trade_id)
    candidate = type("CandidateTrade", (), trade_fields)()
    candidate.id = exclude_trade_id
    combined = sorted([*trades, candidate], key=lambda trade: trade.timestamp)

    if len(combined) > 2:
        return False, "DAILY_LIMIT", "Max 2 trades reached for this trade date."

    return True, "CLEAR", "Discipline engine cleared this trade."


def log_event(user_id, event_type, message, severity="info"):
    log = DisciplineLog(
        user_id=user_id,
        event_type=event_type,
        severity=severity,
        message=message,
    )
    db.session.add(log)
    return log


def status_for_user(user_id):
    trades = today_trades(user_id)
    allowed, code, message = _rule_status(trades)
    losses = len([trade for trade in trades if _net_pnl_inr(trade) < 0])
    wins = len([trade for trade in trades if _net_pnl_inr(trade) > 0])
    score = max(35, 100 - max(0, len(trades) - 1) * 12 - losses * 16)
    if code != "CLEAR":
        score = min(score, 72)

    return {
        "allowed": allowed,
        "code": code,
        "message": message,
        "today_count": len(trades),
        "wins": wins,
        "losses": losses,
        "score": score,
    }
