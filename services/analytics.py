from collections import defaultdict
from datetime import datetime

from models import CapitalTransaction, Expense, Trade

DELTA_USD_INR_RATE = 85


def _money(value):
    return round(float(value or 0), 2)


def _pnl_inr(trade):
    return (trade.pnl * DELTA_USD_INR_RATE) - float(trade.brokerage or 0)


def _gross_pnl_inr(trade):
    return trade.pnl * DELTA_USD_INR_RATE


def capital_summary(user):
    trades = Trade.query.filter_by(user_id=user.id).all()
    transactions = CapitalTransaction.query.filter_by(user_id=user.id).all()
    deposits = sum(transaction.amount for transaction in transactions if transaction.transaction_type == "deposit")
    withdrawals = sum(transaction.amount for transaction in transactions if transaction.transaction_type == "withdrawal")
    gross_pnl = sum(_gross_pnl_inr(trade) for trade in trades)
    brokerage = sum(float(trade.brokerage or 0) for trade in trades)
    net_pnl = gross_pnl - brokerage
    starting_capital = float(user.starting_capital or 0)
    return {
        "starting_capital": _money(starting_capital),
        "deposits": _money(deposits),
        "withdrawals": _money(withdrawals),
        "gross_pnl": _money(gross_pnl),
        "brokerage": _money(brokerage),
        "net_pnl": _money(net_pnl),
        "current_capital": _money(starting_capital + deposits - withdrawals + net_pnl),
    }


def trading_analytics(user):
    trades = Trade.query.filter_by(user_id=user.id).order_by(Trade.timestamp.asc()).all()
    expenses = Expense.query.filter_by(user_id=user.id).all()
    capital = capital_summary(user)
    pnl_values = [_pnl_inr(trade) for trade in trades]
    wins = [value for value in pnl_values if value > 0]
    losses = [value for value in pnl_values if value < 0]

    equity = []
    running = 0
    for trade in trades:
        running += _pnl_inr(trade)
        equity.append({"label": trade.timestamp.strftime("%d %b"), "value": _money(running)})

    daily = defaultdict(float)
    weekly = defaultdict(float)
    monthly = defaultdict(float)
    emotions = defaultdict(lambda: {"pnl": 0.0, "count": 0})
    for trade in trades:
        pnl = _pnl_inr(trade)
        daily[trade.timestamp.strftime("%d %b")] += pnl
        weekly[f"{trade.timestamp.isocalendar().year}-W{trade.timestamp.isocalendar().week:02d}"] += pnl
        monthly[trade.timestamp.strftime("%b %Y")] += pnl
        emotions[trade.emotion]["pnl"] += pnl
        emotions[trade.emotion]["count"] += 1

    expense_categories = defaultdict(float)
    for expense in expenses:
        expense_categories[expense.category] += expense.amount

    gross_profit = sum(wins)
    gross_loss = abs(sum(losses))
    avg_profit = sum(wins) / len(wins) if wins else 0
    avg_loss = sum(losses) / len(losses) if losses else 0

    return {
        "summary": {
            "total_pnl": _money(sum(pnl_values)),
            "gross_pnl": capital["gross_pnl"],
            "total_brokerage": capital["brokerage"],
            "current_capital": capital["current_capital"],
            "starting_capital": capital["starting_capital"],
            "deposits": capital["deposits"],
            "withdrawals": capital["withdrawals"],
            "total_trades": len(trades),
            "win_rate": round((len(wins) / len(trades)) * 100, 1) if trades else 0,
            "avg_profit": _money(avg_profit),
            "avg_loss": _money(avg_loss),
            "risk_reward_ratio": round((gross_profit / gross_loss), 2) if gross_loss else round(gross_profit, 2),
            "best_trade": _money(max(pnl_values)) if pnl_values else 0,
            "total_expenses": _money(sum(expense.amount for expense in expenses)),
        },
        "charts": {
            "equity_curve": equity or [{"label": datetime.utcnow().strftime("%d %b"), "value": 0}],
            "daily_pl": [{"label": key, "value": _money(value)} for key, value in daily.items()],
            "weekly_pl": [{"label": key, "value": _money(value)} for key, value in weekly.items()],
            "monthly_pl": [{"label": key, "value": _money(value)} for key, value in monthly.items()],
            "win_loss": {"wins": len(wins), "losses": len(losses)},
            "emotion_performance": [
                {
                    "label": emotion,
                    "value": _money(data["pnl"] / data["count"]),
                    "count": data["count"],
                }
                for emotion, data in emotions.items()
            ],
            "expense_categories": [
                {"label": key, "value": _money(value)} for key, value in expense_categories.items()
            ],
        },
    }
