# ===============================
# Diagnostic Routes
# Trigger diagnostics and view diagnostic history
# Checklist item: #36
# ===============================

from flask import request, jsonify
from backend.config import app, db
from backend.routes.auth import login_required, get_current_user
from backend.models.session import Session
from backend.models.diagnostic_log import DiagnosticLog
from backend.services.diagnostic_service import diagnose_throw


# ---------------------------------------------
# POST /api/sessions/<id>/diagnose
# Trigger diagnostic on latest throw
# ---------------------------------------------
@app.route('/api/sessions/<int:session_id>/diagnose', methods=['POST'])
@login_required
def trigger_diagnostic(session_id):
    """
    Run diagnostics on the latest throw in a session.

    Optionally specify a roll_id to diagnose a specific throw.

    Body (JSON, optional):
      roll_id — specific roll to diagnose (defaults to latest)

    Returns per-throw rotation diagnostics and any trend alerts.
    """
    try:
        user = get_current_user()
        if not user:
            return jsonify({"error": "User not found"}), 404

        session = Session.query.get(session_id)
        if not session:
            return jsonify({"error": "Session not found"}), 404
        if session.user_id != user.id:
            return jsonify({"error": "Not your session"}), 403

        data = request.get_json(silent=True) or {}
        roll_id = data.get("roll_id")

        result = diagnose_throw(session_id, roll_id)

        if "error" in result:
            return jsonify({"error": result["error"]}), 400

        return jsonify(result), 200

    except Exception as e:
        app.logger.error(f"Diagnostic error: {str(e)}")
        return jsonify({"error": "Failed to run diagnostics"}), 500


# ---------------------------------------------
# GET /api/sessions/<id>/diagnostics
# List all diagnostic alerts for a session
# ---------------------------------------------
@app.route('/api/sessions/<int:session_id>/diagnostics', methods=['GET'])
@login_required
def list_diagnostics(session_id):
    """
    List all diagnostic alerts generated during a session.

    Query params:
      category — filter by category (optional)
      level    — filter by level: info/warning/alert (optional)
    """
    try:
        user = get_current_user()
        if not user:
            return jsonify({"error": "User not found"}), 404

        session = Session.query.get(session_id)
        if not session:
            return jsonify({"error": "Session not found"}), 404
        if session.user_id != user.id:
            return jsonify({"error": "Not your session"}), 403

        query = DiagnosticLog.query.filter_by(session_id=session_id)

        category = request.args.get("category")
        level = request.args.get("level")
        if category:
            query = query.filter_by(category=category)
        if level:
            query = query.filter_by(level=level)

        logs = query.order_by(DiagnosticLog.timestamp.asc()).all()

        return jsonify({
            "diagnostics": [log.to_dict() for log in logs],
            "count": len(logs),
        }), 200

    except Exception as e:
        app.logger.error(f"List diagnostics error: {str(e)}")
        return jsonify({"error": "Failed to list diagnostics"}), 500
