from models import Trade


def calculate_achievements(user_id):
    """
    Calculates progress and unlock status for all trading milestones.
    """
    trades = Trade.query.filter_by(user_id=user_id).order_by(Trade.timestamp.asc()).all()
    total_trades = len(trades)
    net_pnl = sum([t.pnl * 85 for t in trades])  # PnL in INR
    winning_trades = [t for t in trades if t.pnl > 0]
    total_r = sum([t.risk_reward for t in winning_trades])
    win_rate = round((len(winning_trades) / total_trades) * 100, 1) if total_trades > 0 else 0

    # Calculate consecutive green days
    consecutive_green_days = 0
    current_green_streak = 0
    daily_pnls = {}
    for t in trades:
        day_key = t.timestamp.strftime("%Y-%m-%d")
        daily_pnls[day_key] = daily_pnls.get(day_key, 0.0) + t.pnl

    for day_key in sorted(daily_pnls.keys()):
        if daily_pnls[day_key] > 0:
            current_green_streak += 1
            if current_green_streak > consecutive_green_days:
                consecutive_green_days = current_green_streak
        else:
            current_green_streak = 0

    milestones = [
        {
            "id": "first_trade",
            "title": "First Trade Logged",
            "icon": "🚀",
            "description": "Log your first trade entry in the OS",
            "target": 1,
            "current": min(total_trades, 1),
            "unlocked": total_trades >= 1,
            "progress_pct": 100 if total_trades >= 1 else 0,
        },
        {
            "id": "hundred_trades",
            "title": "100 Trades Completed",
            "icon": "🏅",
            "description": "Build a robust sample size of 100 trades",
            "target": 100,
            "current": min(total_trades, 100),
            "unlocked": total_trades >= 100,
            "progress_pct": min(100, int((total_trades / 100) * 100)),
        },
        {
            "id": "ten_green_days",
            "title": "10 Consecutive Green Days",
            "icon": "🟩",
            "description": "Achieve 10 consecutive profitable sessions",
            "target": 10,
            "current": min(consecutive_green_days, 10),
            "unlocked": consecutive_green_days >= 10,
            "progress_pct": min(100, int((consecutive_green_days / 10) * 100)),
        },
        {
            "id": "thirty_discipline",
            "title": "30 Days Without Rule Violation",
            "icon": "🥇",
            "description": "Maintain perfect discipline for 30 sessions",
            "target": 30,
            "current": min(total_trades, 30),
            "unlocked": total_trades >= 30,
            "progress_pct": min(100, int((total_trades / 30) * 100)),
        },
        {
            "id": "ten_r_profit",
            "title": "First 10R Profit",
            "icon": "🎯",
            "description": "Accumulate 10 R-multiplier units in profit",
            "target": 10,
            "current": round(min(total_r, 10), 1),
            "unlocked": total_r >= 10,
            "progress_pct": min(100, int((total_r / 10) * 100)),
        },
        {
            "id": "lakh_profit",
            "title": "₹1 Lakh Profit Milestone",
            "icon": "💰",
            "description": "Cross ₹1,00,000 net profit milestone",
            "target": 100000,
            "current": round(max(0, net_pnl), 2),
            "unlocked": net_pnl >= 100000,
            "progress_pct": min(100, int((max(0, net_pnl) / 100000) * 100)),
        },
        {
            "id": "high_win_rate",
            "title": "Highest Win Rate (60%+)",
            "icon": "⚡",
            "description": "Maintain a 60%+ win rate over 20+ trades",
            "target": 60,
            "current": win_rate if total_trades >= 20 else 0,
            "unlocked": win_rate >= 60 and total_trades >= 20,
            "progress_pct": min(100, int((win_rate / 60) * 100)) if total_trades >= 20 else 0,
        },
    ]

    return milestones
