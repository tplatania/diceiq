# ===============================
# DiceIQ — Main Application
# Backend entry point
# ===============================

from flask import jsonify, request
from flask_compress import Compress
from sqlalchemy import text
from backend.config import app, db

# Enable gzip compression
Compress(app)

# Import routes to register them
import backend.routes

print("--- DiceIQ Backend Starting ---")

# Print registered routes for debugging
print("\n=== REGISTERED ROUTES ===")
for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
    print(f"  {', '.join(rule.methods - {'OPTIONS', 'HEAD'}):20s} {rule.rule}")
print("=== END ROUTES ===\n")

# ---------------------------------------------
# Basic Routes
# ---------------------------------------------

@app.route("/api")
def api_home():
    return jsonify({"message": "Welcome to the DiceIQ API", "version": "1.0.0"})


@app.route("/health")
def health():
    """Health check — tests database connection"""
    import os
    ok_db = True
    db_name = os.environ.get("DB_NAME", "sqlite-local")
    user_count = 0
    try:
        result = db.session.execute(text("SELECT COUNT(*) FROM users"))
        user_count = result.scalar()
    except Exception:
        ok_db = False
    return jsonify({"ok": ok_db, "db": ok_db, "db_name": db_name, "user_count": user_count})


# ---------------------------------------------
# Database Initialization (SQLite dev only)
# ---------------------------------------------
_db_initialized = False

@app.before_request
def initialize_database():
    global _db_initialized
    from backend.config import INSTANCE_CONNECTION_NAME
    if not _db_initialized and not INSTANCE_CONNECTION_NAME:
        with app.app_context():
            db.create_all()
            # FIX: Seed built-in dice sets on first run — was never being called
            try:
                from backend.services.dice_sets_seed import seed_dice_sets
                from backend.models.dice_set import DiceSet
                seed_dice_sets(db, DiceSet)
            except Exception as e:
                app.logger.warning(f"Dice set seeding skipped: {e}")
        _db_initialized = True


# ---------------------------------------------
# Entry Point
# ---------------------------------------------
if __name__ == "__main__":
    import socket
    def get_local_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "localhost"

    local_ip = get_local_ip()
    print("\n" + "=" * 50)
    print("  DiceIQ API is RUNNING")
    print("=" * 50)
    print(f"\n  Local:   http://localhost:5000")
    print(f"  Network: http://{local_ip}:5000")
    print(f"  Health:  http://localhost:5000/health")
    print("=" * 50 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
