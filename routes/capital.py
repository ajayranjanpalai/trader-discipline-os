from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from models import CapitalTransaction, User, db
from services.analytics import capital_summary

capital_bp = Blueprint("capital", __name__)


def _payload():
    return request.get_json(silent=True) or {}


@capital_bp.get("")
@jwt_required()
def get_capital():
    user = User.query.get_or_404(int(get_jwt_identity()))
    transactions = CapitalTransaction.query.filter_by(user_id=user.id).order_by(CapitalTransaction.created_at.desc()).all()
    return {
        "summary": capital_summary(user),
        "transactions": [transaction.to_dict() for transaction in transactions],
    }


@capital_bp.put("/settings")
@jwt_required()
def update_capital_settings():
    user = User.query.get_or_404(int(get_jwt_identity()))
    data = _payload()
    try:
        user.starting_capital = float(data.get("starting_capital", user.starting_capital) or 0)
    except (TypeError, ValueError):
        return {"error": "Starting capital must be a valid number."}, 400
    db.session.commit()
    return {"summary": capital_summary(user), "user": user.to_dict()}


@capital_bp.post("/transactions")
@jwt_required()
def add_capital_transaction():
    user_id = int(get_jwt_identity())
    data = _payload()
    transaction_type = str(data.get("transaction_type") or "").lower()
    if transaction_type not in {"deposit", "withdrawal"}:
        return {"error": "Choose deposit or withdrawal."}, 400
    try:
        amount = float(data.get("amount") or 0)
    except (TypeError, ValueError):
        return {"error": "Amount must be a valid number."}, 400
    if amount <= 0:
        return {"error": "Amount must be greater than zero."}, 400

    transaction = CapitalTransaction(
        user_id=user_id,
        transaction_type=transaction_type,
        amount=amount,
        note=(data.get("note") or "").strip(),
    )
    db.session.add(transaction)
    db.session.commit()
    user = User.query.get_or_404(user_id)
    return {"transaction": transaction.to_dict(), "summary": capital_summary(user)}, 201


@capital_bp.delete("/transactions/<int:transaction_id>")
@jwt_required()
def delete_capital_transaction(transaction_id):
    user_id = int(get_jwt_identity())
    transaction = CapitalTransaction.query.filter_by(id=transaction_id, user_id=user_id).first_or_404()
    db.session.delete(transaction)
    db.session.commit()
    user = User.query.get_or_404(user_id)
    return {"message": "Capital transaction deleted.", "summary": capital_summary(user)}
