from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from services.statistics import generate_calendar_heatmap, generate_day_time_statistics
from models import Trade

heatmap_bp = Blueprint("heatmap_bp", __name__)


@heatmap_bp.route("/calendar", methods=["GET"])
@jwt_required()
def get_calendar_heatmap():
    user_id = int(get_jwt_identity())
    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int)
    data = generate_calendar_heatmap(user_id, month=month, year=year)
    return jsonify(data), 200


@heatmap_bp.route("/day-time", methods=["GET"])
@jwt_required()
def get_day_time_stats():
    user_id = int(get_jwt_identity())
    data = generate_day_time_statistics(user_id)
    return jsonify(data), 200


@heatmap_bp.route("/matrix", methods=["GET"])
@jwt_required()
def get_heatmap_matrix():
    user_id = int(get_jwt_identity())
    trades = Trade.query.filter_by(user_id=user_id).all()
    pairs = {}

    for t in trades:
        symbol = t.pair.upper()
        if symbol not in pairs:
            pairs[symbol] = {"pnl": 0.0, "trades": 0, "wins": 0}
        pairs[symbol]["pnl"] += t.pnl
        pairs[symbol]["trades"] += 1
        if t.pnl > 0:
            pairs[symbol]["wins"] += 1

    out = []
    for symbol, stats in pairs.items():
        wr = round((stats["wins"] / stats["trades"]) * 100, 1) if stats["trades"] > 0 else 0
        out.append({
            "symbol": symbol,
            "pnl": round(stats["pnl"], 2),
            "trades": stats["trades"],
            "win_rate": wr,
            "status": "profit" if stats["pnl"] > 0 else ("loss" if stats["pnl"] < 0 else "breakeven"),
        })

    return jsonify(out), 200
