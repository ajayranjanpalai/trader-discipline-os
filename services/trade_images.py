from models import Trade, db


def get_gallery_trades(user_id, gallery_type="all", tag=None, symbol=None, setup=None):
    """
    Fetches trades with multi-stage screenshots and filters by collection/tags.
    """
    query = Trade.query.filter_by(user_id=user_id)

    if gallery_type == "best":
        query = query.filter((Trade.is_best_trade == True) | (Trade.pnl > 0))
    elif gallery_type == "worst":
        query = query.filter((Trade.is_worst_trade == True) | (Trade.pnl < 0))
    elif gallery_type == "favorite":
        query = query.filter_by(is_favorite=True)

    if symbol:
        query = query.filter(Trade.pair.ilike(f"%{symbol}%"))
    if tag:
        query = query.filter(Trade.tags.ilike(f"%{tag}%"))
    if setup:
        query = query.filter(Trade.trade_reason.ilike(f"%{setup}%"))

    trades = query.order_by(Trade.timestamp.desc()).all()

    result = []
    for t in trades:
        d = t.to_dict()
        d["before_img"] = t.before_img or t.screenshot_url
        d["during_img"] = t.during_img
        d["exit_img"] = t.exit_img
        result.append(d)

    return result
