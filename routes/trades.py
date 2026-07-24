from datetime import datetime

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from models import Trade, db
from services.discipline import log_event, status_for_user, validate_trade_day

trades_bp = Blueprint("trades", __name__)
DELTA_USD_INR_RATE = 85


def _payload():
    return request.get_json(silent=True) or {}


def _parse_time(value):
    if not value:
        return datetime.utcnow()
    return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)


def _trade_fields(data):
    required = ["pair", "direction", "entry", "exit", "stop_loss", "position_size", "pnl", "risk_reward", "emotion"]
    missing = [field for field in required if data.get(field) in (None, "")]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    position_size = float(data["position_size"])
    closed_quantity_raw = data.get("closed_quantity")
    closed_quantity = position_size if closed_quantity_raw in (None, "") else float(closed_quantity_raw)
    if closed_quantity > position_size:
        raise ValueError("Closed quantity cannot exceed position size")

    return {
        "pair": str(data["pair"]).upper(),
        "direction": str(data["direction"]).lower(),
        "entry": float(data["entry"]),
        "exit": float(data["exit"]),
        "stop_loss": float(data["stop_loss"]),
        "position_size": position_size,
        "closed_quantity": closed_quantity,
        "remaining_quantity": max(0.0, position_size - closed_quantity),
        "pnl": float(data["pnl"]),
        "brokerage": float(data.get("brokerage") or 0),
        "risk_reward": float(data["risk_reward"]),
        "emotion": str(data["emotion"]).lower(),
        "trade_reason": data.get("trade_reason", ""),
        "notes": data.get("notes", ""),
        "timestamp": _parse_time(data.get("timestamp")),
    }


@trades_bp.get("")
@jwt_required()
def list_trades():
    user_id = int(get_jwt_identity())
    trades = Trade.query.filter_by(user_id=user_id).order_by(Trade.timestamp.desc()).all()
    return {"trades": [trade.to_dict() for trade in trades], "discipline": status_for_user(user_id)}


@trades_bp.post("")
@jwt_required()
def add_trade():
    user_id = int(get_jwt_identity())
    try:
        fields = _trade_fields(_payload())
    except ValueError as error:
        return {"error": str(error)}, 400

    allowed, code, message = validate_trade_day(user_id, fields)
    if not allowed:
        log_event(user_id, code, message, "danger")
        db.session.commit()
        return {"error": message, "discipline": status_for_user(user_id)}, 403

    trade = Trade(user_id=user_id, **fields)
    db.session.add(trade)
    net_pnl = (trade.pnl * DELTA_USD_INR_RATE) - (trade.brokerage or 0)
    severity = "success" if net_pnl > 0 else "warning"
    log_event(user_id, "TRADE_LOGGED", f"{trade.pair} {trade.direction} logged with net P/L INR {net_pnl:.2f}.", severity)
    db.session.commit()
    return {"trade": trade.to_dict(), "discipline": status_for_user(user_id)}, 201


@trades_bp.put("/<int:trade_id>")
@jwt_required()
def update_trade(trade_id):
    user_id = int(get_jwt_identity())
    trade = Trade.query.filter_by(id=trade_id, user_id=user_id).first_or_404()
    try:
        fields = _trade_fields(_payload())
        allowed, _code, message = validate_trade_day(user_id, fields, exclude_trade_id=trade.id)
        if not allowed:
            return {"error": message, "discipline": status_for_user(user_id)}, 403
        for key, value in fields.items():
            setattr(trade, key, value)
    except ValueError as error:
        return {"error": str(error)}, 400
    db.session.commit()
    return {"trade": trade.to_dict(), "discipline": status_for_user(user_id)}


@trades_bp.delete("/<int:trade_id>")
@jwt_required()
def delete_trade(trade_id):
    user_id = int(get_jwt_identity())
    trade = Trade.query.filter_by(id=trade_id, user_id=user_id).first_or_404()
    db.session.delete(trade)
    db.session.commit()
    return {"message": "Trade deleted.", "discipline": status_for_user(user_id)}


@trades_bp.get("/discipline")
@jwt_required()
def discipline():
    return {"discipline": status_for_user(int(get_jwt_identity()))}
