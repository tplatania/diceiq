# ===============================
# Voice Session Tokens
# HMAC-signed tokens for secure ElevenLabs user identity
# Fixes the raw user_id vulnerability found in SongcraftPro
# ===============================

import hmac
import hashlib
import time
import json
import base64
from backend.config import VOICE_TOKEN_SECRET

TOKEN_EXPIRY_SECONDS = 4 * 60 * 60  # 4 hours


def create_voice_session_token(user_id, session_id):
    """
    Create an HMAC-signed token containing user_id and session_id.
    This token is passed to ElevenLabs when the widget initializes,
    and included in every tool call back to our API.
    """
    payload = {
        "uid": user_id,
        "sid": session_id,
        "exp": int(time.time()) + TOKEN_EXPIRY_SECONDS,
    }
    payload_bytes = json.dumps(payload, separators=(',', ':')).encode('utf-8')
    payload_b64 = base64.urlsafe_b64encode(payload_bytes).decode('utf-8')

    signature = hmac.new(
        VOICE_TOKEN_SECRET.encode('utf-8'),
        payload_b64.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    return f"{payload_b64}.{signature}"


def verify_voice_session_token(token):
    """
    Verify token signature and expiry.
    Returns (user_id, session_id) tuple or (None, None) if invalid.
    """
    try:
        parts = token.split('.')
        if len(parts) != 2:
            return None, None

        payload_b64, provided_sig = parts

        # Verify signature
        expected_sig = hmac.new(
            VOICE_TOKEN_SECRET.encode('utf-8'),
            payload_b64.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(provided_sig, expected_sig):
            return None, None

        # Decode payload
        payload_bytes = base64.urlsafe_b64decode(payload_b64)
        payload = json.loads(payload_bytes)

        # Check expiry
        if time.time() > payload.get("exp", 0):
            return None, None

        return payload.get("uid"), payload.get("sid")

    except Exception:
        return None, None
