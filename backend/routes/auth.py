# ===============================
# Authentication Routes
# JWT token-based (same pattern as SongcraftPro)
# ===============================

import jwt
import re
import secrets
from datetime import datetime, timezone, timedelta
from flask import request, jsonify, g
from functools import wraps
from backend.config import app, db, limiter
from backend.models.user import User
from backend.models.user_stats import UserStats

# JWT Configuration
JWT_SECRET = app.config['SECRET_KEY']
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_DAYS = 30


def create_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.now(timezone.utc) + timedelta(days=JWT_EXPIRATION_DAYS),
        'iat': datetime.now(timezone.utc)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authentication required"}), 401
        token = auth_header.split(' ')[1]
        user_id = verify_token(token)
        if not user_id:
            return jsonify({"error": "Invalid or expired token"}), 401
        # Store user in flask.g so routes don't re-parse the token
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 401
        g.current_user = user
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """Get the current authenticated user. Use after @login_required."""
    return getattr(g, 'current_user', None)


# ---------------------------------------------
# Signup
# ---------------------------------------------
@app.route('/api/auth/signup', methods=['POST'])
@limiter.limit("10 per minute")
def signup():
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Request must be JSON"}), 400

        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        display_name = data.get('display_name', '').strip()

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
            return jsonify({"error": "Invalid email format"}), 400
        if len(password) < 8:
            return jsonify({"error": "Password must be at least 8 characters"}), 400
        if len(password) > 128:
            return jsonify({"error": "Password must be 128 characters or fewer"}), 400

        existing = User.query.filter_by(email=email).first()
        if existing:
            return jsonify({"error": "Email already registered"}), 409

        user = User(email=email, display_name=display_name or email.split('@')[0])
        user.set_password(password)
        db.session.add(user)
        db.session.flush()  # Get user.id before creating stats

        # Create UserStats row for pre-computed lifetime stats
        stats = UserStats(user_id=user.id)
        db.session.add(stats)
        db.session.commit()

        token = create_token(user.id)
        return jsonify({
            "message": "Account created successfully",
            "token": token,
            "user": user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Signup error: {str(e)}")
        return jsonify({"error": "Failed to create account"}), 500


# ---------------------------------------------
# Login
# ---------------------------------------------
@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Request must be JSON"}), 400

        email = data.get('email', '').strip().lower()
        password = data.get('password', '')

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return jsonify({"error": "Invalid email or password"}), 401

        user.last_login = datetime.now(timezone.utc).replace(tzinfo=None)
        db.session.commit()

        token = create_token(user.id)
        return jsonify({
            "message": "Login successful",
            "token": token,
            "user": user.to_dict()
        }), 200
    except Exception as e:
        app.logger.error(f"Login error: {str(e)}")
        return jsonify({"error": "Login failed"}), 500


# ---------------------------------------------
# Current User
# ---------------------------------------------
@app.route('/api/auth/me', methods=['GET'])
@login_required
def get_me():
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": user.to_dict()}), 200


# ---------------------------------------------
# Forgot / Reset Password
# ---------------------------------------------
@app.route('/api/auth/forgot-password', methods=['POST'])
@limiter.limit("5 per minute")
def forgot_password():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request must be JSON"}), 400
    email = data.get('email', '').strip().lower()
    # Always return success to prevent email enumeration
    if email:
        user = User.query.filter_by(email=email).first()
        if user:
            reset_token = secrets.token_urlsafe(32)
            user.reset_token = reset_token
            user.reset_token_expires = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=1)
            db.session.commit()
            # TODO: send_password_reset_email(email, reset_url)
    return jsonify({"message": "If an account exists, you will receive a reset link."}), 200


@app.route('/api/auth/reset-password', methods=['POST'])
@limiter.limit("5 per minute")
def reset_password():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request must be JSON"}), 400

    token = data.get('token', '').strip()
    new_password = data.get('password', '')

    if not token or not new_password or len(new_password) < 8:
        return jsonify({"error": "Valid token and password (8+ chars) required"}), 400
    if len(new_password) > 128:
        return jsonify({"error": "Password must be 128 characters or fewer"}), 400

    user = User.query.filter_by(reset_token=token).first()
    if not user or not user.reset_token_expires or user.reset_token_expires < datetime.now(timezone.utc).replace(tzinfo=None):
        return jsonify({"error": "Invalid or expired reset link"}), 400

    user.set_password(new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.session.commit()
    return jsonify({"message": "Password reset successfully"}), 200
