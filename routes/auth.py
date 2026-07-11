import re

from flask import Blueprint, request
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required

from models import User, db

auth_bp = Blueprint("auth", __name__)
jwt = JWTManager()
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@auth_bp.record_once
def init_jwt(state):
    jwt.init_app(state.app)


def _payload():
    return request.get_json(silent=True) or {}


def _signup_fields():
    data = _payload()
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    return data, name, email, password


@auth_bp.post("/signup")
def signup():
    _data, name, email, password = _signup_fields()
    if not name or not email or len(password) < 6 or not EMAIL_RE.match(email):
        return {"error": "Name, valid email, and 6+ character password are required."}, 400
    if User.query.filter_by(email=email).first():
        return {"error": "Email is already registered."}, 409

    user = User(name=name, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    token = create_access_token(identity=str(user.id))
    return {"message": "Account created.", "token": token, "user": user.to_dict()}, 201


@auth_bp.post("/login")
def login():
    data = _payload()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return {"error": "Invalid email or password."}, 401

    token = create_access_token(identity=str(user.id))
    return {"token": token, "user": user.to_dict()}


@auth_bp.get("/me")
@jwt_required()
def me():
    user = User.query.get_or_404(int(get_jwt_identity()))
    return {"user": user.to_dict()}
