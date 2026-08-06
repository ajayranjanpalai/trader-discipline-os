import csv
import io
from models import Trade


def export_trades_csv(user_id):
    """
    Generates a CSV export stream for all user trades.
    """
    trades = Trade.query.filter_by(user_id=user_id).order_by(Trade.timestamp.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "ID", "Timestamp", "Pair", "Direction", "Entry", "Exit",
        "Stop Loss", "Position Size", "Net PnL INR", "Risk Reward",
        "Emotion", "Setup / Reason", "Notes", "Tags"
    ])

    for t in trades:
        writer.writerow([
            t.id,
            t.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            t.pair,
            t.direction,
            t.entry,
            t.exit,
            t.stop_loss,
            t.position_size,
            round((t.pnl * 85) - (t.brokerage or 0), 2),
            t.risk_reward,
            t.emotion,
            t.trade_reason or "",
            t.notes or "",
            t.tags or "",
        ])

    output.seek(0)
    return output.getvalue()
