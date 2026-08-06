from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from services.achievements import calculate_achievements

milestone_bp = Blueprint("milestone_bp", __name__)


@milestone_bp.route("", methods=["GET"])
@jwt_required()
def get_user_milestones():
    user_id = int(get_jwt_identity())
    achievements = calculate_achievements(user_id)
    return jsonify(achievements), 200
