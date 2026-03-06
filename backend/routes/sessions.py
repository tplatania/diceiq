# ===============================
# Session Routes
# Create, list, view, and end practice/play sessions
# Checklist items: #23-26
# ===============================

from datetime import datetime, timezone
from flask import request, jsonify
from backend.config import app, db
from backend.routes.auth import login_required, get_current_user
from backend.models.session import Session
from backend.models.hand import Hand
from backend.models.roll import Roll
from backend.models.dice_set import DiceSet
from backend.models.user_stats import UserStats
from backend.models.shooter_signature import ShooterSignature


# ---------------------------------------------
# POST /api/sessions — Create a new session
# ---------------------------------------------
@app.route('/api/sessions', methods=['POST'])
@login_required
def create_session():
    """
    Start a new practice or play session.

    Body (JSON):
      mode         — "practice" or "play" (default: practice)
      dice_set_id  — which set to use (optional, uses user preferred if omitted)
      location     — where they are practicing (optional)
      bankroll_start — starting bankroll for play mode (optional)
      table_type   — "hard" / "standard" / "soft" (optional, stored as session metadata)
      notes        — any opening notes (optional)

    A user can only have one active session at a time.
    Attempting to start a new session while one is active returns 409.
    """
    try:
        user = get_current_user()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Enforce single active session per user
        active = Session.query.filter_by(
            user_id=user.id, status="active"
        ).first()
        if active:
            return jsonify({
                "error": "You already have an active session",
                "active_session_id": active.id,
                "hint": "End your current session before starting a new one."
            }), 409

        data = request.get_json() or {}
        mode = data.get("mode", "practice")
        if mode not in ("practice", "play"):
            return jsonify({"error": "Mode must be 'practice' or 'play'"}), 400

        # Resolve dice set — explicit, user preferred, or None
        dice_set_id = data.get("dice_set_id")
        if dice_set_id:
            dice_set = DiceSet.query.get(dice_set_id)
            if not dice_set:
                return jsonify({"error": "Dice set not found"}), 404
            # Custom sets must belong to this user
            if dice_set.user_id and dice_set.user_id != user.id:
                return jsonify({"error": "You do not own this dice set"}), 403
        elif user.preferred_dice_set:
            # Fallback to user's preferred set by name
            preferred = DiceSet.query.filter_by(name=user.preferred_dice_set).first()
            if preferred:
                dice_set_id = preferred.id

        session = Session(
            user_id=user.id,
            mode=mode,
            status="active",
            dice_set_id=dice_set_id,
            location=data.get("location"),
            bankroll_start=data.get("bankroll_start"),
            notes=data.get("notes"),
        )
        db.session.add(session)
        db.session.commit()

        return jsonify({
            "message": "Session started",
            "session": session.summary()
        }), 201

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Create session error: {str(e)}")
        return jsonify({"error": "Failed to create session"}), 500


# ---------------------------------------------
# GET /api/sessions — List all sessions for user
# ---------------------------------------------
@app.route('/api/sessions', methods=['GET'])
@login_required
def list_sessions():
    """
    List all sessions for the logged-in user.
    Paginated, newest first.

    Query params:
      page    — page number (default 1)
      per_page — results per page (default 20, max 100)
      status  — filter by status: active / completed / all (default: all)
      mode    — filter by mode: practice / play / all (default: all)
    """
    try:
        user = get_current_user()
        if not user:
            return jsonify({"error": "User not found"}), 404

        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 20, type=int), 100)
        status_filter = request.args.get("status", "all")
        mode_filter = request.args.get("mode", "all")

        query = Session.query.filter_by(user_id=user.id)

        if status_filter != "all":
            query = query.filter_by(status=status_filter)
        if mode_filter != "all":
            query = query.filter_by(mode=mode_filter)

        query = query.order_by(Session.started_at.desc())
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            "sessions": [s.summary() for s in paginated.items],
            "pagination": {
                "page": paginated.page,
                "per_page": paginated.per_page,
                "total": paginated.total,
                "pages": paginated.pages,
                "has_next": paginated.has_next,
                "has_prev": paginated.has_prev,
            }
        }), 200

    except Exception as e:
        app.logger.error(f"List sessions error: {str(e)}")
        return jsonify({"error": "Failed to list sessions"}), 500


# ---------------------------------------------
# GET /api/sessions/<id> — Get single session
# ---------------------------------------------
@app.route('/api/sessions/<int:session_id>', methods=['GET'])
@login_required
def get_session(session_id):
    """
    Get a single session with all hands and rolls.
    Only the owner can view their sessions.

    Returns full session detail including:
      - Session metadata and summary stats
      - All hands with outcomes
      - All rolls with face/rotation data
      - Dice set info
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

        # Build hands list
        hands_data = []
        for hand in sorted(session.hands, key=lambda h: h.hand_number):
            hands_data.append({
                "id": hand.id,
                "hand_number": hand.hand_number,
                "point": hand.point,
                "outcome": hand.outcome,
                "roll_count": hand.roll_count,
                "started_at": hand.started_at.isoformat() if hand.started_at else None,
                "ended_at": hand.ended_at.isoformat() if hand.ended_at else None,
            })

        # Build rolls list
        rolls_data = [r.to_dict() for r in sorted(session.rolls, key=lambda r: r.roll_number)]

        # Dice set info
        dice_set_data = None
        if session.dice_set_id:
            dice_set = DiceSet.query.get(session.dice_set_id)
            if dice_set:
                dice_set_data = dice_set.to_dict()

        # Live SRR for active sessions (from running counters)
        live_srr = None
        live_axis_pct = None
        if session.status == "active":
            if session.total_sevens and session.total_sevens > 0:
                live_srr = round(session.total_rolls / session.total_sevens, 2)
            if session.total_rolls and session.total_rolls > 0:
                live_axis_pct = round(((session.total_on_axis or 0) / session.total_rolls) * 100, 1)

        return jsonify({
            "session": {
                **session.summary(),
                "bankroll_start": session.bankroll_start,
                "bankroll_end": session.bankroll_end,
                "avg_hand_length": session.avg_hand_length,
                "notes": session.notes,
                "total_sevens": session.total_sevens,
                "total_doubles": session.total_doubles,
                "total_on_axis": session.total_on_axis,
                "current_hand_rolls": session.current_hand_rolls,
                "live_srr": live_srr,
                "live_axis_pct": live_axis_pct,
            },
            "dice_set": dice_set_data,
            "hands": hands_data,
            "rolls": rolls_data,
            "roll_count": len(rolls_data),
            "hand_count": len(hands_data),
        }), 200

    except Exception as e:
        app.logger.error(f"Get session error: {str(e)}")
        return jsonify({"error": "Failed to get session"}), 500


# ---------------------------------------------
# PATCH /api/sessions/<id> — Update a session
# ---------------------------------------------
@app.route('/api/sessions/<int:session_id>', methods=['PATCH'])
@login_required
def update_session(session_id):
    """
    Update a session. Handles multiple update scenarios:

    1. End session — send { "action": "end" }
       Finalizes stats, updates UserStats, increments throws_since_last_compute.
       Does NOT recompute signature (user-triggered only).

    2. Update metadata — send any of:
       bankroll_end, notes, location, dice_set_id

    3. Abandon session — send { "action": "abandon" }
       Marks session as abandoned without computing final stats.

    Returns updated session summary.
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

        data = request.get_json() or {}
        action = data.get("action")

        # ── Action: End Session ──────────────────────────────────────
        if action == "end":
            if session.status != "active":
                return jsonify({"error": "Session is not active"}), 400

            # Apply any final metadata updates
            if "bankroll_end" in data:
                session.bankroll_end = data["bankroll_end"]
            if "notes" in data:
                session.notes = data["notes"]

            # Finalize session stats (SRR, axis %, avg hand length)
            session.finalize()

            # Update lifetime stats
            stats = UserStats.query.filter_by(user_id=user.id).first()
            if stats:
                stats.update_from_session(session)

            # Flag signature for recompute suggestion
            # The actual suggestion logic compares lifetime rolls vs analyzed throws
            sig = ShooterSignature.query.filter_by(user_id=user.id).first()
            if sig:
                sig.needs_recompute = True

            db.session.commit()

            # Build response with signature suggestion if applicable
            response = {
                "message": "Session ended",
                "session": session.summary(),
                "stats_updated": True,
            }

            # Check if we should suggest a signature recompute
            if sig and sig.needs_recompute:
                # Count rolls WITH face/rotation data (not all rolls)
                # Only these are usable for signature computation
                from sqlalchemy import func
                face_data_count = (
                    db.session.query(func.count(Roll.id))
                    .join(Session, Roll.session_id == Session.id)
                    .filter(Session.user_id == user.id)
                    .filter(Roll.left_x_rotation.isnot(None))
                    .scalar()
                ) or 0
                analyzed = sig.total_throws_analyzed or 0
                unprocessed = face_data_count - analyzed

                if unprocessed >= 20:
                    response["signature_suggestion"] = {
                        "suggest_recompute": True,
                        "unprocessed_throws": unprocessed,
                        "message": (
                            f"I have {unprocessed} new throws since your last "
                            f"signature update. I have enough data to refine "
                            f"your recommendation. Would you like me to "
                            f"recompute your signature?"
                        ),
                    }

            return jsonify(response), 200

        # ── Action: Abandon Session ──────────────────────────────────
        elif action == "abandon":
            if session.status != "active":
                return jsonify({"error": "Session is not active"}), 400

            session.status = "abandoned"
            session.ended_at = datetime.now(timezone.utc).replace(tzinfo=None)
            db.session.commit()

            return jsonify({
                "message": "Session abandoned",
                "session": session.summary(),
            }), 200

        # ── Metadata Update (no action specified) ────────────────────
        else:
            if session.status != "active":
                return jsonify({"error": "Cannot update a completed session"}), 400

            if "bankroll_end" in data:
                session.bankroll_end = data["bankroll_end"]
            if "notes" in data:
                session.notes = data["notes"]
            if "location" in data:
                session.location = data["location"]
            if "dice_set_id" in data:
                new_set_id = data["dice_set_id"]
                if new_set_id:
                    dice_set = DiceSet.query.get(new_set_id)
                    if not dice_set:
                        return jsonify({"error": "Dice set not found"}), 404
                    if dice_set.user_id and dice_set.user_id != user.id:
                        return jsonify({"error": "You do not own this dice set"}), 403
                session.dice_set_id = new_set_id

            db.session.commit()

            return jsonify({
                "message": "Session updated",
                "session": session.summary(),
            }), 200

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Update session error: {str(e)}")
        return jsonify({"error": "Failed to update session"}), 500
