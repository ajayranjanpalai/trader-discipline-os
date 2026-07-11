from collections import defaultdict

from models import AIInsight, Trade, db


RISK_EMOTIONS = {"fomo", "revenge", "greedy", "fearful"}
DELTA_USD_INR_RATE = 85


def _pnl_inr(trade):
    return (trade.pnl * DELTA_USD_INR_RATE) - float(trade.brokerage or 0)


def generate_insights(user_id):
    trades = Trade.query.filter_by(user_id=user_id).order_by(Trade.timestamp.asc()).all()
    insights = []

    if not trades:
        return [
            {
                "insight_type": "onboarding",
                "title": "Awaiting Trade Data",
                "message": "Log a few trades and the AI engine will begin detecting behavior patterns.",
                "confidence": 70,
                "severity": "info",
            }
        ]

    risky = [trade for trade in trades if trade.emotion.lower() in RISK_EMOTIONS]
    if risky:
        avg_risky = sum(_pnl_inr(trade) for trade in risky) / len(risky)
        insights.append(
            {
                "insight_type": "emotional_trading",
                "title": "Emotional Trading Pressure",
                "message": f"{len(risky)} trades were logged under high-risk emotions. Average P/L during those trades is INR {avg_risky:.2f}.",
                "confidence": min(96, 65 + len(risky) * 6),
                "severity": "warning" if avg_risky < 0 else "info",
            }
        )

    revenge_trades = [trade for trade in trades if trade.emotion.lower() == "revenge"]
    if revenge_trades:
        insights.append(
            {
                "insight_type": "revenge_trading",
                "title": "Revenge Trading Detected",
                "message": "Trades tagged as revenge entries show impulse risk. Add a cooldown before placing the next order.",
                "confidence": 92,
                "severity": "danger",
            }
        )

    fomo_trades = [trade for trade in trades if trade.emotion.lower() == "fomo"]
    if fomo_trades:
        insights.append(
            {
                "insight_type": "fomo",
                "title": "FOMO Pattern",
                "message": "FOMO entries are present in your journal. Require a written setup reason before execution.",
                "confidence": 88,
                "severity": "warning",
            }
        )

    daily_counts = defaultdict(int)
    for trade in trades:
        daily_counts[trade.timestamp.date().isoformat()] += 1
    overtrade_days = [day for day, count in daily_counts.items() if count > 2]
    if overtrade_days:
        insights.append(
            {
                "insight_type": "overtrading",
                "title": "Overtrading Risk",
                "message": f"{len(overtrade_days)} day(s) exceeded the 2-trade discipline limit.",
                "confidence": 95,
                "severity": "danger",
            }
        )

    hours = defaultdict(lambda: {"pnl": 0.0, "count": 0})
    for trade in trades:
        label = f"{trade.timestamp.hour:02d}:00"
        hours[label]["pnl"] += _pnl_inr(trade)
        hours[label]["count"] += 1
    best_hour = max(hours.items(), key=lambda item: item[1]["pnl"] / item[1]["count"])
    insights.append(
        {
            "insight_type": "best_time",
            "title": "Best Trading Window",
            "message": f"Your strongest logged trading hour is around {best_hour[0]}, based on average P/L.",
            "confidence": 78,
            "severity": "success",
        }
    )

    AIInsight.query.filter_by(user_id=user_id).delete()
    saved = []
    for item in insights:
        model = AIInsight(user_id=user_id, **item)
        db.session.add(model)
        saved.append(model)
    db.session.commit()
    return [item.to_dict() for item in saved]
