from datetime import datetime, timedelta
from models import Trade


def generate_calendar_heatmap(user_id, month=None, year=None):
    """
    Generates a color-coded daily calendar matrix for a given user.
    Statuses: 'profit' (🟩), 'loss' (🟥), 'breakeven' (🟨), 'no_trade'
    """
    now = datetime.utcnow()
    target_year = year or now.year
    target_month = month or now.month

    trades = Trade.query.filter_by(user_id=user_id).all()
    daily_stats = {}

    for t in trades:
        if t.timestamp.year == target_year and t.timestamp.month == target_month:
            day_str = t.timestamp.strftime("%Y-%m-%d")
            if day_str not in daily_stats:
                daily_stats[day_str] = {"pnl": 0.0, "trades": 0, "wins": 0}
            daily_stats[day_str]["pnl"] += t.pnl
            daily_stats[day_str]["trades"] += 1
            if t.pnl > 0:
                daily_stats[day_str]["wins"] += 1

    calendar_days = []
    for day, stats in daily_stats.items():
        if stats["pnl"] > 0:
            status = "profit"
        elif stats["pnl"] < 0:
            status = "loss"
        else:
            status = "breakeven"

        calendar_days.append({
            "date": day,
            "pnl": round(stats["pnl"], 2),
            "trades": stats["trades"],
            "status": status,
        })

    return calendar_days


def generate_day_time_statistics(user_id):
    """
    Computes performance aggregated by Day-of-Week (Mon-Fri) and Time-of-Day.
    """
    trades = Trade.query.filter_by(user_id=user_id).all()
    days_map = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}
    dow_stats = {name: {"pnl": 0.0, "trades": 0, "wins": 0} for name in days_map.values()}

    time_stats = {
        "Morning (9-12)": {"pnl": 0.0, "trades": 0, "wins": 0},
        "Mid-Day (12-15)": {"pnl": 0.0, "trades": 0, "wins": 0},
        "Closing (15-18)": {"pnl": 0.0, "trades": 0, "wins": 0},
        "Night (18-24)": {"pnl": 0.0, "trades": 0, "wins": 0},
    }

    for t in trades:
        dow = days_map[t.timestamp.weekday()]
        dow_stats[dow]["pnl"] += t.pnl
        dow_stats[dow]["trades"] += 1
        if t.pnl > 0:
            dow_stats[dow]["wins"] += 1

        hour = t.timestamp.hour
        if 9 <= hour < 12:
            time_key = "Morning (9-12)"
        elif 12 <= hour < 15:
            time_key = "Mid-Day (12-15)"
        elif 15 <= hour < 18:
            time_key = "Closing (15-18)"
        else:
            time_key = "Night (18-24)"

        time_stats[time_key]["pnl"] += t.pnl
        time_stats[time_key]["trades"] += 1
        if t.pnl > 0:
            time_stats[time_key]["wins"] += 1

    return {
        "day_of_week": dow_stats,
        "time_of_day": time_stats,
    }
