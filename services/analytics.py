from collections import defaultdict
from datetime import datetime, timedelta

from models import CapitalTransaction, Expense, Task, Trade

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


def _trade_dict(trade):
    return {
        "id": trade.id,
        "pair": trade.pair,
        "direction": trade.direction,
        "entry": trade.entry,
        "exit": trade.exit,
        "remaining_exit": trade.remaining_exit,
        "stop_loss": trade.stop_loss,
        "position_size": trade.position_size,
        "closed_quantity": trade.closed_quantity or 0,
        "remaining_quantity": trade.remaining_quantity or 0,
        "pnl": trade.pnl,
        "brokerage": trade.brokerage or 0,
        "risk_reward": trade.risk_reward,
        "emotion": trade.emotion,
        "trade_reason": trade.trade_reason or "",
        "notes": trade.notes or "",
        "timestamp": trade.timestamp.isoformat(),
        "created_at": trade.created_at.isoformat(),
    }


def _expense_dict(expense):
    return {
        "id": expense.id,
        "title": expense.title,
        "amount": expense.amount,
        "category": expense.category,
        "payment_method": expense.payment_method,
        "note": expense.note or "",
        "timestamp": expense.timestamp.isoformat(),
    }


def _capital_transaction_dict(transaction):
    return {
        "id": transaction.id,
        "transaction_type": transaction.transaction_type,
        "amount": transaction.amount,
        "note": transaction.note or "",
        "created_at": transaction.created_at.isoformat(),
    }


def _task_dict(task):
    completion_dates = {completion.completed_on.isoformat() for completion in task.completions}
    if task.completed_at:
        completion_dates.add(task.completed_at.date().isoformat())
    return {
        "id": task.id,
        "title": task.title,
        "category": task.category,
        "task_scope": task.task_scope or "today",
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "completed": task.completed,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        "completion_dates": sorted(completion_dates),
        "created_at": task.created_at.isoformat(),
    }


def trading_analytics(user):
    trades = Trade.query.filter_by(user_id=user.id).order_by(Trade.timestamp.asc()).all()
    expenses = Expense.query.filter_by(user_id=user.id).all()
    transactions = CapitalTransaction.query.filter_by(user_id=user.id).all()
    tasks = Task.query.filter_by(user_id=user.id).order_by(Task.created_at.desc()).all()
    capital = capital_summary(user)
    pnl_values = [_pnl_inr(trade) for trade in trades]
    wins = [value for value in pnl_values if value > 0]
    losses = [value for value in pnl_values if value < 0]

    equity_events = []
    for trade in trades:
        equity_events.append((trade.timestamp, _pnl_inr(trade), "equity"))
    for transaction in transactions:
        amount = transaction.amount if transaction.transaction_type == "deposit" else -transaction.amount
        equity_events.append((transaction.created_at, amount, transaction.transaction_type))

    equity_events.sort(key=lambda event: event[0])
    equity = []
    running = capital["starting_capital"]
    if equity_events:
        start_date = equity_events[0][0] - timedelta(days=1)
        equity.append({
            "label": start_date.strftime("%d %b"),
            "date": start_date.isoformat(),
            "value": _money(running),
            "type": "equity",
        })
        for timestamp, delta, event_type in equity_events:
            running += delta
            equity.append({
                "label": timestamp.strftime("%d %b"),
                "date": timestamp.isoformat(),
                "value": _money(running),
                "type": event_type,
            })
    else:
        now = datetime.utcnow()
        equity = [
            {
                "label": (now - timedelta(days=1)).strftime("%d %b"),
                "date": (now - timedelta(days=1)).isoformat(),
                "value": capital["starting_capital"],
                "type": "equity",
            },
            {
                "label": now.strftime("%d %b"),
                "date": now.isoformat(),
                "value": capital["current_capital"],
                "type": "equity",
            },
        ]

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
            "equity_curve": equity,
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
        "capital": {
            "summary": capital,
            "transactions": [_capital_transaction_dict(transaction) for transaction in sorted(transactions, key=lambda item: item.created_at, reverse=True)],
        },
        "lists": {
            "trades": [_trade_dict(trade) for trade in sorted(trades, key=lambda item: item.timestamp, reverse=True)],
            "expenses": [_expense_dict(expense) for expense in sorted(expenses, key=lambda item: item.timestamp, reverse=True)],
            "tasks": [_task_dict(task) for task in tasks],
        },
    }
