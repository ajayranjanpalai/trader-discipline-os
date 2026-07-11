from flask import Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required

from models import User
from services.analytics import trading_analytics

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.get("")
@jwt_required()
def analytics():
    user = User.query.get_or_404(int(get_jwt_identity()))
    return trading_analytics(user)
