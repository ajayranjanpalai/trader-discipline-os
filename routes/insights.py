from flask import Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required

from models import AIInsight
from services.ai import generate_insights

insights_bp = Blueprint("insights", __name__)


@insights_bp.get("")
@jwt_required()
def list_insights():
    user_id = int(get_jwt_identity())
    existing = AIInsight.query.filter_by(user_id=user_id).order_by(AIInsight.created_at.desc()).all()
    if not existing:
        return {"insights": generate_insights(user_id)}
    return {"insights": [insight.to_dict() for insight in existing]}


@insights_bp.post("/generate")
@jwt_required()
def refresh_insights():
    return {"insights": generate_insights(int(get_jwt_identity()))}
