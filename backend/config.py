# ===============================
# DiceIQ — Configuration Module
# Flask, DB, API keys, connection pooling, caching
# Mirrors SongcraftPro pattern with critical improvements
# ===============================

import os
import re
import logging
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Load environment variables FIRST
load_dotenv()

print("--- DICEIQ VERSION: 1.0.0 (SaaS Foundation) ---")

# ---------------------------------------------
# Flask & CORS Setup
# ---------------------------------------------
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app = Flask(__name__, root_path=_project_root)
app.logger.setLevel(logging.DEBUG)

# Session configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'diceiq-dev-secret-change-in-production')
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 86400 * 30  # 30 days

CORS(
    app,
    resources={
        r"/*": {
            "origins": [
                re.compile(r"^http://localhost(?::\d+)?$"),
                re.compile(r"^http://127\.0\.0\.1(?::\d+)?$"),
                re.compile(r"^http://10\.\d+\.\d+\.\d+(?::\d+)?$"),
                re.compile(r"^http://192\.168\.\d+\.\d+(?::\d+)?$"),
                re.compile(r"^https://.*\.run\.app$"),
                re.compile(r"^https://diceiq\.net$"),
                re.compile(r"^https://www\.diceiq\.net$"),
            ],
            "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
        }
    },
)

app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB max upload

# ---------------------------------------------
# Rate Limiting
# ---------------------------------------------
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["60 per minute"],
    storage_uri="memory://",
)

# ---------------------------------------------
# Caching (SimpleCache for single-instance, upgrade to Redis later if needed)
# ---------------------------------------------
cache = Cache(app, config={
    'CACHE_TYPE': 'SimpleCache',
    'CACHE_DEFAULT_TIMEOUT': 60,  # 60 second default TTL
})

# ---------------------------------------------
# Voice Session Token Secret (separate from JWT secret)
# ---------------------------------------------
VOICE_TOKEN_SECRET = os.environ.get('VOICE_TOKEN_SECRET', 'diceiq-voice-dev-secret')

# ---------------------------------------------
# Production Secret Safety Check
# Refuse to start if production is using default dev secrets
# ---------------------------------------------
_is_production = os.environ.get('FLASK_ENV') == 'production' or os.environ.get('ENV') == 'production'
if _is_production:
    if app.config['SECRET_KEY'] == 'diceiq-dev-secret-change-in-production':
        raise RuntimeError("FATAL: SECRET_KEY is still the default dev value. Set SECRET_KEY env var for production.")
    if VOICE_TOKEN_SECRET == 'diceiq-voice-dev-secret':
        raise RuntimeError("FATAL: VOICE_TOKEN_SECRET is still the default dev value. Set VOICE_TOKEN_SECRET env var for production.")

# ---------------------------------------------
# ElevenLabs Setup
# ---------------------------------------------
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
ELEVENLABS_AGENT_ID = os.environ.get("ELEVENLABS_AGENT_ID", "")
ELEVENLABS_SERVER_SECRET = os.environ.get("ELEVENLABS_SERVER_SECRET")

if ELEVENLABS_API_KEY:
    ELEVENLABS_API_KEY = ELEVENLABS_API_KEY.strip()
    print(f"--- ElevenLabs key loaded (ends with: ...{ELEVENLABS_API_KEY[-4:]}) ---")
else:
    print("--- WARNING: No ElevenLabs API key found! ---")

if ELEVENLABS_SERVER_SECRET:
    ELEVENLABS_SERVER_SECRET = ELEVENLABS_SERVER_SECRET.strip()
    print(f"--- ElevenLabs server secret loaded ---")
else:
    print("--- WARNING: No ElevenLabs server secret found! ---")

# ---------------------------------------------
# Cloud Storage Setup
# ---------------------------------------------
GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME")

storage_client = None
bucket = None
try:
    if GCS_BUCKET_NAME:
        from google.cloud import storage
        storage_client = storage.Client()
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        print(f"--- GCS bucket: {GCS_BUCKET_NAME} ---")
except Exception as e:
    print(f"--- GCS not available (local dev): {e} ---")

# ---------------------------------------------
# Database Configuration
# Cloud SQL (production) or SQLite (local dev)
# With proper connection pooling
# ---------------------------------------------
INSTANCE_CONNECTION_NAME = os.environ.get("INSTANCE_CONNECTION_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_NAME = os.environ.get("DB_NAME")

if INSTANCE_CONNECTION_NAME and DB_USER and DB_PASS and DB_NAME:
    print("--- Cloud SQL: connector mode ---")
    from google.cloud.sql.connector import Connector, IPTypes
    connector = Connector()

    def getconn():
        return connector.connect(
            INSTANCE_CONNECTION_NAME,
            "pg8000",
            user=DB_USER,
            password=DB_PASS,
            db=DB_NAME,
            ip_type=IPTypes.PUBLIC,
        )

    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+pg8000://"
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "creator": getconn,
        "pool_size": 10,
        "max_overflow": 20,
        "pool_timeout": 30,
        "pool_recycle": 1800,
        "pool_pre_ping": True,
    }
else:
    print("--- SQLite: local dev mode ---")
    SQLITE_PATH = os.path.join(_project_root, "diceiq.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{SQLITE_PATH}"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy and Migrate
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ---------------------------------------------
# Stripe Setup
# ---------------------------------------------
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")

if STRIPE_SECRET_KEY:
    print(f"--- Stripe key loaded (ends with: ...{STRIPE_SECRET_KEY.strip()[-4:]}) ---")
else:
    print("--- WARNING: No Stripe key found! ---")
