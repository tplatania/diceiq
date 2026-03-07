# ===============================
# Route Decorators
# ElevenLabs secret verification, auth helpers
# ===============================

from functools import wraps
from flask import jsonify, request
from backend.config import app, ELEVENLABS_SERVER_SECRET


def require_elevenlabs_secret(f):
    """
    Verify ElevenLabs server secret on tool endpoints.
    Same pattern as SongcraftPro but with added logging.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        provided_secret = request.headers.get("X-Server-Secret") or request.args.get("server_secret")

        if not ELEVENLABS_SERVER_SECRET:
            app.logger.error(f"ELEVENLABS_SERVER_SECRET not configured - {f.__name__} blocked!")
            return jsonify({"error": "Service unavailable - server secret not configured"}), 503

        if not provided_secret:
            app.logger.warning(f"Unauthorized: no secret for {f.__name__}")
            return jsonify({"error": "Unauthorized - server secret required"}), 401

        if provided_secret.strip() != ELEVENLABS_SERVER_SECRET:
            app.logger.warning(f"Unauthorized: invalid secret for {f.__name__}")
            return jsonify({"error": "Unauthorized - invalid server secret"}), 401

        return f(*args, **kwargs)
    return decorated_function
