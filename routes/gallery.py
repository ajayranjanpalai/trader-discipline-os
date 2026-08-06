from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from services.trade_images import get_gallery_trades
from models import Trade, db

gallery_bp = Blueprint("gallery_bp", __name__)


@gallery_bp.route("/trades", methods=["GET"])
@jwt_required()
def list_gallery_trades():
    user_id = int(get_jwt_identity())
    gtype = request.args.get("type", "all")
    tag = request.args.get("tag")
    symbol = request.args.get("symbol")
    setup = request.args.get("setup")

    trades = get_gallery_trades(user_id, gallery_type=gtype, tag=tag, symbol=symbol, setup=setup)
    return jsonify(trades), 200


@gallery_bp.route("/trades/<int:trade_id>/favorite", methods=["POST"])
@jwt_required()
def toggle_favorite_trade(trade_id):
    user_id = int(get_jwt_identity())
    trade = Trade.query.filter_by(id=trade_id, user_id=user_id).first_or_404()
    trade.is_favorite = not trade.is_favorite
    db.session.commit()
    return jsonify({"id": trade.id, "is_favorite": trade.is_favorite}), 200
