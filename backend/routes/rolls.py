# ===============================
# Roll Entry Routes
# Log rolls, batch import, list rolls
# Checklist items: #27-29
# ===============================

from datetime import datetime, timezone
from flask import request, jsonify
from backend.config import app, db
from backend.routes.auth import login_required, get_current_user
from backend.models.session import Session
from backend.models.roll import Roll
from backend.models.hand import Hand
from backend.models.dice_set import DiceSet
from backend.services.dice_orientation import (
    calculate_rotations, is_valid_orientation
)


# -----------------------------------------------
# Constants
# -----------------------------------------------
VALID_FACES = {1, 2, 3, 4, 5, 6}
COME_OUT_NATURALS = {7, 11}
COME_OUT_CRAPS = {2, 3, 12}
POINT_NUMBERS = {4, 5, 6, 8, 9, 10}


# -----------------------------------------------
# Helper: Process a single roll
# -----------------------------------------------
def _process_roll(session, data, roll_number):
    """
    Process a single roll entry. Handles:
    - Validation
    - On-axis calculation against active dice set
    - Rotation calculation from face capture
    - Game state management (play mode)
    - Running counter updates on session

    Returns (roll_dict, error_string).
    If error_string is not None, the roll was rejected.
    """
    left_die = data.get("left_die")
    right_die = data.get("right_die")

    # Validate die values
    if left_die not in VALID_FACES or right_die not in VALID_FACES:
        return None, "left_die and right_die must be integers 1-6"

    total = left_die + right_die
    is_double = left_die == right_die
    is_seven = total == 7

    # ── Face capture (optional) ──────────────────────────────
    left_top = data.get("left_top_face")
    left_front = data.get("left_front_face")
    right_top = data.get("right_top_face")
    right_front = data.get("right_front_face")

    has_face_data = all(v is not None for v in [left_top, left_front, right_top, right_front])

    # Validate face data if provided
    if has_face_data:
        for val, label in [(left_top, "left_top_face"), (left_front, "left_front_face"),
                           (right_top, "right_top_face"), (right_front, "right_front_face")]:
            if val not in VALID_FACES:
                return None, f"{label} must be integer 1-6"
        # Top face must match die value
        if left_top != left_die:
            return None, f"left_top_face ({left_top}) must match left_die ({left_die})"
        if right_top != right_die:
            return None, f"right_top_face ({right_top}) must match right_die ({right_die})"
        # Validate orientation is physically possible
        if not is_valid_orientation(left_top, left_front):
            return None, f"Invalid left die orientation: top={left_top}, front={left_front}"
        if not is_valid_orientation(right_top, right_front):
            return None, f"Invalid right die orientation: top={right_top}, front={right_front}"

    # ── Rotation calculation ─────────────────────────────────
    left_x = left_y = left_z = None
    right_x = right_y = right_z = None
    left_sig = right_sig = None

    # Fetch dice set once — used for both rotation calc and on-axis check
    dice_set = None
    if session.dice_set_id:
        dice_set = DiceSet.query.get(session.dice_set_id)

    if has_face_data and dice_set and dice_set.top_faces and dice_set.front_faces:
            # Starting orientation from the dice set definition
            start_left_top = dice_set.top_faces.get("left")
            start_left_front = dice_set.front_faces.get("left")
            start_right_top = dice_set.top_faces.get("right")
            start_right_front = dice_set.front_faces.get("right")

            if start_left_top and start_left_front:
                left_rot = calculate_rotations(
                    start_left_top, start_left_front,
                    left_top, left_front
                )
                if left_rot.get("valid"):
                    left_x = left_rot["x"]
                    left_y = left_rot["y"]
                    left_z = left_rot["z"]
                    left_sig = left_rot["signature"]

            if start_right_top and start_right_front:
                right_rot = calculate_rotations(
                    start_right_top, start_right_front,
                    right_top, right_front
                )
                if right_rot.get("valid"):
                    right_x = right_rot["x"]
                    right_y = right_rot["y"]
                    right_z = right_rot["z"]
                    right_sig = right_rot["signature"]

    # ── On-axis check ────────────────────────────────────────
    on_axis = None
    if dice_set and dice_set.on_axis_outcomes:
            # On-axis if total appears in the set's on-axis distribution
            # AND Y/Z are zero (true axis control)
            # If we have rotation data, true on-axis means Y=0 and Z=0
            if left_y is not None and right_y is not None:
                on_axis = (left_y == 0 and left_z == 0 and
                           right_y == 0 and right_z == 0)
            else:
                # Fallback: doubles count as on-axis (basic check)
                on_axis = is_double

    # ── Game state (play mode) ───────────────────────────────
    phase = None
    point = None
    result_type = None
    hand_id = None

    if session.mode == "play":
        # Find or create the current hand
        current_hand = Hand.query.filter_by(
            session_id=session.id, outcome="in_progress"
        ).first()

        if not current_hand:
            # Start a new hand — we're on come-out
            session.total_hands += 1
            current_hand = Hand(
                session_id=session.id,
                hand_number=session.total_hands,
            )
            db.session.add(current_hand)
            db.session.flush()

        hand_id = current_hand.id
        current_hand.roll_count += 1

        if current_hand.point is None:
            # ── Come-out phase ──
            phase = "come_out"
            if total in COME_OUT_NATURALS:
                result_type = "natural"
                current_hand.outcome = "natural"
                current_hand.ended_at = datetime.now(timezone.utc).replace(tzinfo=None)
            elif total in COME_OUT_CRAPS:
                result_type = "craps"
                current_hand.outcome = "craps"
                current_hand.ended_at = datetime.now(timezone.utc).replace(tzinfo=None)
            elif total in POINT_NUMBERS:
                result_type = "point_set"
                current_hand.point = total
                point = total
        else:
            # ── Point phase ──
            phase = "point"
            point = current_hand.point
            if total == current_hand.point:
                result_type = "point_made"
                current_hand.outcome = "point_made"
                current_hand.ended_at = datetime.now(timezone.utc).replace(tzinfo=None)
            elif total == 7:
                result_type = "seven_out"
                current_hand.outcome = "seven_out"
                current_hand.ended_at = datetime.now(timezone.utc).replace(tzinfo=None)
            else:
                result_type = "number"

    # ── Create the Roll record ───────────────────────────────
    roll = Roll(
        session_id=session.id,
        hand_id=hand_id,
        roll_number=roll_number,
        left_die=left_die,
        right_die=right_die,
        total=total,
        phase=phase,
        point=point,
        result_type=result_type,
        is_double=is_double,
        on_axis=on_axis,
        # Face capture
        left_top_face=left_top,
        left_front_face=left_front,
        right_top_face=right_top,
        right_front_face=right_front,
        # Rotation analysis
        left_x_rotation=left_x,
        left_y_rotation=left_y,
        left_z_rotation=left_z,
        right_x_rotation=right_x,
        right_y_rotation=right_y,
        right_z_rotation=right_z,
        left_rotation_sig=left_sig,
        right_rotation_sig=right_sig,
    )
    db.session.add(roll)

    # ── Update session running counters ──────────────────────
    session.total_rolls += 1
    session.last_roll_at = datetime.now(timezone.utc).replace(tzinfo=None)

    if is_seven:
        session.total_sevens += 1
    if is_double:
        session.total_doubles += 1
    if on_axis:
        session.total_on_axis += 1
    if total in (4, 5, 6, 8, 9, 10):
        session.total_box_numbers += 1

    # Update per-number distribution (powers bet strategy engine)
    dist = session.number_distribution or {str(n): 0 for n in range(2, 13)}
    dist[str(total)] = dist.get(str(total), 0) + 1
    session.number_distribution = dist

    # Track current hand length and longest hand
    session.current_hand_rolls += 1
    if session.current_hand_rolls > session.longest_hand:
        session.longest_hand = session.current_hand_rolls

    # Reset hand roll counter when a hand ends
    # Play mode: seven-out, natural, craps, or point_made
    # Practice mode: every seven resets the counter (simulated hand)
    if session.mode == "play":
        if result_type in ("seven_out", "natural", "craps", "point_made"):
            session.current_hand_rolls = 0
    else:
        # Practice mode — no game state, but sevens still mark hand boundaries
        if is_seven:
            session.total_hands += 1
            session.current_hand_rolls = 0

    # ── Build live stats for response ────────────────────────
    live_srr = None
    if session.total_sevens > 0:
        live_srr = round(session.total_rolls / session.total_sevens, 2)

    live_axis_pct = None
    if session.total_rolls > 0:
        live_axis_pct = round(((session.total_on_axis or 0) / session.total_rolls) * 100, 1)

    return {
        "roll": roll.to_dict(),
        "game_state": {
            "phase": phase,
            "point": point,
            "result_type": result_type,
        },
        "session_stats": {
            "total_rolls": session.total_rolls,
            "total_sevens": session.total_sevens,
            "total_doubles": session.total_doubles,
            "total_on_axis": session.total_on_axis,
            "current_hand_rolls": session.current_hand_rolls,
            "longest_hand": session.longest_hand,
            "live_srr": live_srr,
            "live_axis_pct": live_axis_pct,
        },
    }, None


# ---------------------------------------------
# POST /api/sessions/<id>/rolls — Log a single roll
# ---------------------------------------------
@app.route('/api/sessions/<int:session_id>/rolls', methods=['POST'])
@login_required
def log_roll(session_id):
    """
    Log a single roll to an active session.

    Body (JSON):
      left_die       — left die face value (1-6, required)
      right_die      — right die face value (1-6, required)
      left_top_face  — left die top face after throw (1-6, optional)
      left_front_face — left die front face after throw (1-6, optional)
      right_top_face — right die top face after throw (1-6, optional)
      right_front_face — right die front face after throw (1-6, optional)

    If all four face values are provided AND a dice set is active,
    the server calculates X/Y/Z rotations automatically.

    Returns the roll data, game state (play mode), and live session stats.
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
        if session.status != "active":
            return jsonify({"error": "Session is not active"}), 400

        # Enforce per-tier roll limit
        roll_limit = user.get_session_limit()
        if session.total_rolls >= roll_limit:
            return jsonify({
                "error": "Roll limit reached for your subscription tier",
                "limit": roll_limit,
                "tier": user.subscription_tier,
                "hint": "Upgrade to Pro for unlimited rolls."
            }), 403

        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body required"}), 400

        roll_number = session.total_rolls + 1
        result, error = _process_roll(session, data, roll_number)

        if error:
            return jsonify({"error": error}), 400

        db.session.commit()
        return jsonify(result), 201

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Log roll error: {str(e)}")
        return jsonify({"error": "Failed to log roll"}), 500


# ---------------------------------------------
# POST /api/sessions/<id>/rolls/batch — Batch roll entry
# ---------------------------------------------
@app.route('/api/sessions/<int:session_id>/rolls/batch', methods=['POST'])
@login_required
def batch_rolls(session_id):
    """
    Log multiple rolls at once (photo import use case).

    Body (JSON):
      rolls — array of roll objects, each with:
        left_die, right_die (required)
        left_top_face, left_front_face, right_top_face, right_front_face (optional)

    Processes rolls in order. If any roll fails validation,
    all previously processed rolls in the batch are still committed.
    The response includes which rolls succeeded and which failed.
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
        if session.status != "active":
            return jsonify({"error": "Session is not active"}), 400

        # Enforce per-tier roll limit
        roll_limit = user.get_session_limit()
        remaining = roll_limit - session.total_rolls
        if remaining <= 0:
            return jsonify({
                "error": "Roll limit reached for your subscription tier",
                "limit": roll_limit,
                "tier": user.subscription_tier,
            }), 403

        data = request.get_json()
        if not data or "rolls" not in data:
            return jsonify({"error": "Request body must contain 'rolls' array"}), 400

        rolls_input = data["rolls"]
        if not isinstance(rolls_input, list) or len(rolls_input) == 0:
            return jsonify({"error": "rolls must be a non-empty array"}), 400

        if len(rolls_input) > 500:
            return jsonify({"error": "Maximum 500 rolls per batch"}), 400

        # Cap batch to remaining roll allowance
        if len(rolls_input) > remaining:
            rolls_input = rolls_input[:remaining]

        results = []
        errors = []

        for i, roll_data in enumerate(rolls_input):
            # Validate each item is a dict
            if not isinstance(roll_data, dict):
                errors.append({"index": i, "error": "Each roll must be a JSON object", "input": roll_data})
                continue

            roll_number = session.total_rolls + 1
            result, error = _process_roll(session, roll_data, roll_number)
            if error:
                errors.append({"index": i, "error": error, "input": roll_data})
            else:
                results.append(result)

        db.session.commit()

        # Return final session stats after all rolls processed
        live_srr = None
        if session.total_sevens > 0:
            live_srr = round(session.total_rolls / session.total_sevens, 2)
        live_axis_pct = None
        if session.total_rolls > 0:
            live_axis_pct = round(((session.total_on_axis or 0) / session.total_rolls) * 100, 1)

        return jsonify({
            "message": f"Processed {len(results)} rolls ({len(errors)} errors)",
            "processed": len(results),
            "errors_count": len(errors),
            "errors": errors if errors else None,
            "session_stats": {
                "total_rolls": session.total_rolls,
                "total_sevens": session.total_sevens,
                "total_doubles": session.total_doubles,
                "total_on_axis": session.total_on_axis,
                "longest_hand": session.longest_hand,
                "live_srr": live_srr,
                "live_axis_pct": live_axis_pct,
            },
        }), 201

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Batch rolls error: {str(e)}")
        return jsonify({"error": "Failed to process batch"}), 500


# ---------------------------------------------
# GET /api/sessions/<id>/rolls — List all rolls
# ---------------------------------------------
@app.route('/api/sessions/<int:session_id>/rolls', methods=['GET'])
@login_required
def list_rolls(session_id):
    """
    List all rolls in a session, ordered by roll number.

    Query params:
      page     — page number (default 1)
      per_page — results per page (default 50, max 500)
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

        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 50, type=int), 500)

        query = Roll.query.filter_by(session_id=session.id).order_by(Roll.roll_number.asc())
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            "rolls": [r.to_dict() for r in paginated.items],
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
        app.logger.error(f"List rolls error: {str(e)}")
        return jsonify({"error": "Failed to list rolls"}), 500
