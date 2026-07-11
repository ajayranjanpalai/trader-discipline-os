from datetime import datetime

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from models import Expense, db

expenses_bp = Blueprint("expenses", __name__)
VALID_CATEGORIES = {"food", "transport", "trading", "shopping", "bills"}
VALID_METHODS = {"cash", "upi", "card"}


@expenses_bp.get("")
@jwt_required()
def list_expenses():
    user_id = int(get_jwt_identity())
    expenses = Expense.query.filter_by(user_id=user_id).order_by(Expense.timestamp.desc()).all()
    return {"expenses": [expense.to_dict() for expense in expenses]}


@expenses_bp.post("")
@jwt_required()
def add_expense():
    data = request.get_json(silent=True) or {}
    category = str(data.get("category", "")).lower()
    method = str(data.get("payment_method", "")).lower()
    if category not in VALID_CATEGORIES or method not in VALID_METHODS:
        return {"error": "Invalid category or payment method."}, 400

    expense = Expense(
        user_id=int(get_jwt_identity()),
        title=(data.get("title") or "Expense").strip(),
        amount=float(data.get("amount") or 0),
        category=category,
        payment_method=method,
        note=data.get("note", ""),
        timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else datetime.utcnow(),
    )
    db.session.add(expense)
    db.session.commit()
    return {"expense": expense.to_dict()}, 201


@expenses_bp.delete("/<int:expense_id>")
@jwt_required()
def delete_expense(expense_id):
    expense = Expense.query.filter_by(id=expense_id, user_id=int(get_jwt_identity())).first_or_404()
    db.session.delete(expense)
    db.session.commit()
    return {"message": "Expense deleted."}
