from datetime import datetime, timedelta
import json
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from models import (
    DailyDiary,
    EconomicEvent,
    LearningResource,
    MarketReplayNote,
    SessionNote,
    Trade,
    TradeTimelineEvent,
    TradingMilestone,
    TradingRule,
    TradingSetup,
    WatchlistItem,
    db,
)

extended_api_bp = Blueprint("extended_api", __name__)

DAILY_QUOTES = [
    {"quote": "Plan your trade and trade your plan.", "author": "Richard Dennis"},
    {"quote": "Risk comes from not knowing what you're doing.", "author": "Warren Buffett"},
    {"quote": "Cutting losses quickly is the single most important rule in trading.", "author": "Paul Tudor Jones"},
    {"quote": "The goal of a successful trader is to make the best trades. Money is secondary.", "author": "Alexander Elder"},
    {"quote": "Discipline is choosing between what you want now and what you want most.", "author": "Augustine"},
    {"quote": "In trading, what is comfortable is rarely profitable.", "author": "Robert Arnott"},
    {"quote": "Emotional control is the true key to market consistency.", "author": "Mark Douglas"},
]


# --- 1. Trade Timeline API ---
@extended_api_bp.route("/timeline/<int:trade_id>", methods=["GET"])
@jwt_required()
def get_trade_timeline(trade_id):
    user_id = int(get_jwt_identity())
    events = (
        TradeTimelineEvent.query.filter_by(user_id=user_id, trade_id=trade_id)
        .order_by(TradeTimelineEvent.timestamp.asc())
        .all()
    )
    return jsonify([e.to_dict() for e in events]), 200


@extended_api_bp.route("/timeline/<int:trade_id>", methods=["POST"])
@jwt_required()
def add_trade_timeline_event(trade_id):
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    action = data.get("action")
    if not action:
        return jsonify({"error": "Action is required"}), 400

    event = TradeTimelineEvent(
        trade_id=trade_id,
        user_id=user_id,
        action=action,
        notes=data.get("notes", ""),
    )
    db.session.add(event)
    db.session.commit()
    return jsonify(event.to_dict()), 201


# --- 2. Market Replay Notes API ---
@extended_api_bp.route("/market-replay", methods=["GET", "POST"])
@jwt_required()
def handle_market_replay():
    user_id = int(get_jwt_identity())
    if request.method == "GET":
        notes = MarketReplayNote.query.filter_by(user_id=user_id).order_by(MarketReplayNote.date.desc()).all()
        return jsonify([n.to_dict() for n in notes]), 200

    data = request.get_json() or {}
    note = MarketReplayNote(
        user_id=user_id,
        date=data.get("date", datetime.utcnow().strftime("%Y-%m-%d")),
        bias=data.get("bias", "Neutral"),
        key_levels=data.get("key_levels", ""),
        lessons=data.get("lessons", ""),
        mistakes=data.get("mistakes", ""),
        what_worked=data.get("what_worked", ""),
    )
    db.session.add(note)
    db.session.commit()
    return jsonify(note.to_dict()), 201


# --- 3. Watchlist Manager API ---
@extended_api_bp.route("/watchlist", methods=["GET", "POST"])
@jwt_required()
def handle_watchlist():
    user_id = int(get_jwt_identity())
    if request.method == "GET":
        category = request.args.get("category")
        query = WatchlistItem.query.filter_by(user_id=user_id)
        if category:
            query = query.filter_by(category=category)
        items = query.order_by(WatchlistItem.symbol.asc()).all()
        return jsonify([item.to_dict() for item in items]), 200

    data = request.get_json() or {}
    symbol = data.get("symbol")
    category = data.get("category", "Crypto")
    if not symbol:
        return jsonify({"error": "Symbol is required"}), 400

    item = WatchlistItem(
        user_id=user_id,
        symbol=symbol.upper(),
        category=category,
        notes=data.get("notes", ""),
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201


@extended_api_bp.route("/watchlist/<int:item_id>", methods=["DELETE"])
@jwt_required()
def delete_watchlist_item(item_id):
    user_id = int(get_jwt_identity())
    item = WatchlistItem.query.filter_by(id=item_id, user_id=user_id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Watchlist item removed"}), 200


# --- 4. Trading Setups & Strategy Versioning API ---
@extended_api_bp.route("/setups", methods=["GET", "POST"])
@jwt_required()
def handle_setups():
    user_id = int(get_jwt_identity())
    if request.method == "GET":
        setups = TradingSetup.query.filter_by(user_id=user_id).order_by(TradingSetup.name.asc()).all()
        return jsonify([s.to_dict() for s in setups]), 200

    data = request.get_json() or {}
    name = data.get("name")
    if not name:
        return jsonify({"error": "Setup name is required"}), 400

    conditions = data.get("conditions", [])
    setup = TradingSetup(
        user_id=user_id,
        name=name,
        version=data.get("version", "v1"),
        category=data.get("category", "General"),
        conditions_json=json.dumps(conditions),
        is_favorite=bool(data.get("is_favorite", False)),
        notes=data.get("notes", ""),
    )
    db.session.add(setup)
    db.session.commit()
    return jsonify(setup.to_dict()), 201


# --- 6. Rule Builder API ---
@extended_api_bp.route("/rules", methods=["GET", "POST"])
@jwt_required()
def handle_rules():
    user_id = int(get_jwt_identity())
    if request.method == "GET":
        rules = TradingRule.query.filter_by(user_id=user_id).all()
        return jsonify([r.to_dict() for r in rules]), 200

    data = request.get_json() or {}
    text = data.get("rule_text")
    if not text:
        return jsonify({"error": "Rule text is required"}), 400

    rule = TradingRule(
        user_id=user_id,
        rule_text=text,
        category=data.get("category", "Discipline"),
        is_active=bool(data.get("is_active", True)),
    )
    db.session.add(rule)
    db.session.commit()
    return jsonify(rule.to_dict()), 201


@extended_api_bp.route("/rules/<int:rule_id>", methods=["DELETE"])
@jwt_required()
def delete_rule(rule_id):
    user_id = int(get_jwt_identity())
    rule = TradingRule.query.filter_by(id=rule_id, user_id=user_id).first_or_404()
    db.session.delete(rule)
    db.session.commit()
    return jsonify({"message": "Rule removed"}), 200


# --- 12 & 13. Daily Diary & Session Notes API ---
@extended_api_bp.route("/diary", methods=["GET", "POST"])
@jwt_required()
def handle_diary():
    user_id = int(get_jwt_identity())
    if request.method == "GET":
        diaries = DailyDiary.query.filter_by(user_id=user_id).order_by(DailyDiary.date.desc()).all()
        return jsonify([d.to_dict() for d in diaries]), 200

    data = request.get_json() or {}
    diary = DailyDiary(
        user_id=user_id,
        date=data.get("date", datetime.utcnow().strftime("%Y-%m-%d")),
        todays_goal=data.get("todays_goal", ""),
        todays_mood=data.get("todays_mood", "Focused"),
        todays_lesson=data.get("todays_lesson", ""),
        tomorrows_focus=data.get("tomorrows_focus", ""),
    )
    db.session.add(diary)
    db.session.commit()
    return jsonify(diary.to_dict()), 201


@extended_api_bp.route("/session-notes", methods=["GET", "POST"])
@jwt_required()
def handle_session_notes():
    user_id = int(get_jwt_identity())
    if request.method == "GET":
        notes = SessionNote.query.filter_by(user_id=user_id).order_by(SessionNote.date.desc()).all()
        return jsonify([n.to_dict() for n in notes]), 200

    data = request.get_json() or {}
    note = SessionNote(
        user_id=user_id,
        date=data.get("date", datetime.utcnow().strftime("%Y-%m-%d")),
        phase=data.get("phase", "Pre-Market"),
        content=data.get("content", ""),
    )
    db.session.add(note)
    db.session.commit()
    return jsonify(note.to_dict()), 201


# --- 30. Economic Event Journal API ---
@extended_api_bp.route("/economic-events", methods=["GET", "POST"])
@jwt_required()
def handle_economic_events():
    user_id = int(get_jwt_identity())
    if request.method == "GET":
        events = EconomicEvent.query.filter_by(user_id=user_id).order_by(EconomicEvent.date.desc()).all()
        return jsonify([e.to_dict() for e in events]), 200

    data = request.get_json() or {}
    event = EconomicEvent(
        user_id=user_id,
        date=data.get("date", datetime.utcnow().strftime("%Y-%m-%d")),
        event_name=data.get("event_name", "Macro Event"),
        market_reaction=data.get("market_reaction", ""),
        trade_taken=data.get("trade_taken", ""),
        lesson_learned=data.get("lesson_learned", ""),
    )
    db.session.add(event)
    db.session.commit()
    return jsonify(event.to_dict()), 201


# --- 29. Learning Hub API ---
@extended_api_bp.route("/learning", methods=["GET", "POST"])
@jwt_required()
def handle_learning():
    user_id = int(get_jwt_identity())
    if request.method == "GET":
        resources = LearningResource.query.filter_by(user_id=user_id).order_by(LearningResource.created_at.desc()).all()
        return jsonify([r.to_dict() for r in resources]), 200

    data = request.get_json() or {}
    resource = LearningResource(
        user_id=user_id,
        title=data.get("title", "Trading Resource"),
        resource_type=data.get("resource_type", "Book"),
        link_or_notes=data.get("link_or_notes", ""),
        status=data.get("status", "To Learn"),
    )
    db.session.add(resource)
    db.session.commit()
    return jsonify(resource.to_dict()), 201


@extended_api_bp.route("/learning/<int:item_id>", methods=["PUT"])
@jwt_required()
def update_learning_status(item_id):
    user_id = int(get_jwt_identity())
    resource = LearningResource.query.filter_by(id=item_id, user_id=user_id).first_or_404()
    data = request.get_json() or {}
    if "status" in data:
        resource.status = data["status"]
    db.session.commit()
    return jsonify(resource.to_dict()), 200


# --- 5. Trading Milestones API ---
@extended_api_bp.route("/milestones", methods=["GET"])
@jwt_required()
def get_milestones():
    user_id = int(get_jwt_identity())
    trades = Trade.query.filter_by(user_id=user_id).all()
    total_trades = len(trades)
    winning_trades = len([t for t in trades if t.pnl > 0])
    total_r = sum([t.risk_reward for t in trades if t.pnl > 0])

    default_milestones = [
        {"title": "First 100 Trades", "description": "Complete 100 logged trades", "target_value": 100, "current_value": min(total_trades, 100)},
        {"title": "100 Winning Trades", "description": "Achieve 100 profitable trades", "target_value": 100, "current_value": min(winning_trades, 100)},
        {"title": "100R Profit", "description": "Accumulate 100 Risk-Reward units in profit", "target_value": 100, "current_value": round(total_r, 2)},
        {"title": "30 Days Discipline", "description": "Trade disciplined for 30 sessions", "target_value": 30, "current_value": min(total_trades, 30)},
        {"title": "60 Days No Rule Break", "description": "Maintain zero rule breaks for 60 sessions", "target_value": 60, "current_value": min(total_trades, 60)},
    ]

    out = []
    for m in default_milestones:
        unlocked = m["current_value"] >= m["target_value"]
        out.append({
            "title": m["title"],
            "description": m["description"],
            "target_value": m["target_value"],
            "current_value": m["current_value"],
            "is_unlocked": unlocked,
            "progress_pct": min(100, int((m["current_value"] / m["target_value"]) * 100)),
        })
    return jsonify(out), 200


# --- 7. Instrument Statistics API ---
@extended_api_bp.route("/instrument-stats", methods=["GET"])
@jwt_required()
def get_instrument_stats():
    user_id = int(get_jwt_identity())
    trades = Trade.query.filter_by(user_id=user_id).all()
    pairs = {}
    for t in trades:
        symbol = t.pair.upper()
        if symbol not in pairs:
            pairs[symbol] = []
        pairs[symbol].append(t)

    result = []
    for symbol, t_list in pairs.items():
        total = len(t_list)
        wins = len([t for t in t_list if t.pnl > 0])
        total_pnl = sum([t.pnl for t in t_list])
        avg_rr = sum([t.risk_reward for t in t_list]) / total if total > 0 else 0
        avg_holding = sum([t.holding_time_minutes for t in t_list]) / total if total > 0 else 0
        win_rate = round((wins / total) * 100, 1) if total > 0 else 0

        result.append({
            "symbol": symbol,
            "total_trades": total,
            "win_rate": win_rate,
            "avg_rr": round(avg_rr, 2),
            "total_pnl": round(total_pnl, 2),
            "avg_holding_minutes": round(avg_holding, 1),
        })

    return jsonify(result), 200


# --- 8. Trade Duration Analysis API ---
@extended_api_bp.route("/duration-analysis", methods=["GET"])
@jwt_required()
def get_duration_analysis():
    user_id = int(get_jwt_identity())
    trades = Trade.query.filter_by(user_id=user_id).all()
    categories = {"Scalp": [], "Intraday": [], "Swing": [], "Position": []}

    for t in trades:
        cat = t.duration_type if t.duration_type in categories else "Intraday"
        categories[cat].append(t)

    out = {}
    for cat, t_list in categories.items():
        total = len(t_list)
        wins = len([t for t in t_list if t.pnl > 0])
        pnl = sum([t.pnl for t in t_list])
        avg_hold = sum([t.holding_time_minutes for t in t_list]) / total if total > 0 else 0
        out[cat] = {
            "total_trades": total,
            "win_rate": round((wins / total) * 100, 1) if total > 0 else 0,
            "net_pnl": round(pnl, 2),
            "avg_holding_minutes": round(avg_hold, 1),
        }

    return jsonify(out), 200


# --- 9. Heatmap Matrix API ---
@extended_api_bp.route("/heatmap", methods=["GET"])
@jwt_required()
def get_heatmap_matrix():
    user_id = int(get_jwt_identity())
    trades = Trade.query.filter_by(user_id=user_id).all()
    matrix = {}

    for t in trades:
        symbol = t.pair.upper()
        if symbol not in matrix:
            matrix[symbol] = {"pnl": 0.0, "trades": 0, "wins": 0}
        matrix[symbol]["pnl"] += t.pnl
        matrix[symbol]["trades"] += 1
        if t.pnl > 0:
            matrix[symbol]["wins"] += 1

    out = []
    for symbol, stats in matrix.items():
        wr = round((stats["wins"] / stats["trades"]) * 100, 1) if stats["trades"] > 0 else 0
        out.append({
            "symbol": symbol,
            "pnl": round(stats["pnl"], 2),
            "trades": stats["trades"],
            "win_rate": wr,
            "status": "profit" if stats["pnl"] > 0 else ("loss" if stats["pnl"] < 0 else "breakeven"),
        })

    return jsonify(out), 200


# --- 21. Daily Trading Quote API ---
@extended_api_bp.route("/quotes/daily", methods=["GET"])
def get_daily_quote():
    day_of_year = datetime.utcnow().timetuple().tm_yday
    quote = DAILY_QUOTES[day_of_year % len(DAILY_QUOTES)]
    return jsonify(quote), 200


# --- 19 & 20. Weekly & Monthly Reports API ---
@extended_api_bp.route("/reports/weekly", methods=["GET"])
@jwt_required()
def get_weekly_report():
    user_id = int(get_jwt_identity())
    now = datetime.utcnow()
    start_of_week = now - timedelta(days=now.weekday())
    trades = Trade.query.filter(
        Trade.user_id == user_id,
        Trade.timestamp >= start_of_week
    ).all()

    total_pnl = sum([t.pnl for t in trades])
    wins = len([t for t in trades if t.pnl > 0])
    total = len(trades)
    win_rate = round((wins / total) * 100, 1) if total > 0 else 0

    best_trade = max(trades, key=lambda t: t.pnl) if trades else None
    worst_trade = min(trades, key=lambda t: t.pnl) if trades else None

    return jsonify({
        "week_start": start_of_week.strftime("%Y-%m-%d"),
        "total_trades": total,
        "weekly_profit": round(total_pnl, 2),
        "win_rate": win_rate,
        "best_trade": best_trade.to_dict() if best_trade else None,
        "worst_trade": worst_trade.to_dict() if worst_trade else None,
    }), 200
