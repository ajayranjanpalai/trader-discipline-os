from datetime import datetime, timedelta
from models import Expense, Trade, User


def generate_comprehensive_report(user_id, period="monthly"):
    """
    Generates a full performance, capital growth, discipline, and psychology report.
    """
    user = User.query.get(user_id)
    now = datetime.utcnow()

    if period == "daily":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "weekly":
        start_date = now - timedelta(days=now.weekday())
    elif period == "yearly":
        start_date = datetime(now.year, 1, 1)
    else:  # monthly
        start_date = datetime(now.year, now.month, 1)

    trades = Trade.query.filter(Trade.user_id == user_id, Trade.timestamp >= start_date).all()
    expenses = Expense.query.filter(Expense.user_id == user_id, Expense.timestamp >= start_date).all()

    total_trades = len(trades)
    wins = [t for t in trades if t.pnl > 0]
    losses = [t for t in trades if t.pnl < 0]
    win_rate = round((len(wins) / total_trades) * 100, 1) if total_trades > 0 else 0

    gross_profit = sum([t.pnl * 85 for t in wins])
    gross_loss = abs(sum([t.pnl * 85 for t in losses]))
    profit_factor = round(gross_profit / gross_loss, 2) if gross_loss > 0 else (gross_profit if gross_profit > 0 else 0.0)
    net_pnl = gross_profit - gross_loss
    total_expenses = sum([e.amount for e in expenses])

    # Find best setup & worst mistake
    setups = {}
    emotions = {}
    for t in trades:
        s = t.trade_reason or "General"
        setups[s] = setups.get(s, 0.0) + t.pnl
        e = t.emotion or "neutral"
        emotions[e] = emotions.get(e, 0.0) + t.pnl

    best_setup = max(setups.items(), key=lambda x: x[1])[0] if setups else "N/A"
    worst_emotion = min(emotions.items(), key=lambda x: x[1])[0] if emotions else "N/A"

    ai_suggestion = "Maintain strict position sizing and avoid revenge trading after two consecutive losses."
    if win_rate >= 65:
        ai_suggestion = "Excellent execution quality! Focus on scaling position size on high-conviction setups."
    elif win_rate < 45:
        ai_suggestion = "Win rate is below threshold. Filter setups and increase pre-trade checklist compliance."

    return {
        "user_name": user.name if user else "Trader",
        "period": period.capitalize(),
        "period_start": start_date.strftime("%Y-%m-%d"),
        "total_trades": total_trades,
        "win_rate": win_rate,
        "profit": round(net_pnl, 2),
        "profit_factor": profit_factor,
        "best_setup": best_setup,
        "worst_mistake": f"Trading under emotion: {worst_emotion}" if worst_emotion != "N/A" else "None",
        "total_expenses": round(total_expenses, 2),
        "net_yield": round(net_pnl - total_expenses, 2),
        "ai_suggestion": ai_suggestion,
    }
