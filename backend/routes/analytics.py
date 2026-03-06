# ===============================
# Analytics Routes
# Session analytics, signature, lifetime stats, progress
# Checklist items: #30-33
# ===============================

from datetime import datetime, timezone
from flask import request, jsonify
from backend.config import app, db
from backend.routes.auth import login_required, get_current_user
from backend.models.session import Session
from backend.models.roll import Roll
from backend.models.hand import Hand
from backend.models.dice_set import DiceSet
from backend.models.user_stats import UserStats
from backend.models.shooter_signature import ShooterSignature
from backend.models.signature_history import SignatureHistory
from backend.models.skill_progression import SkillProgression
from backend.models.user import User


# -----------------------------------------------
# Expected random distribution for each total
# Used to compute signature numbers (hot/cold)
# -----------------------------------------------
RANDOM_DISTRIBUTION = {
    2:  1/36,   # 2.78%
    3:  2/36,   # 5.56%
    4:  3/36,   # 8.33%
    5:  4/36,   # 11.11%
    6:  5/36,   # 13.89%
    7:  6/36,   # 16.67%
    8:  5/36,   # 13.89%
    9:  4/36,   # 11.11%
    10: 3/36,   # 8.33%
    11: 2/36,   # 5.56%
    12: 1/36,   # 2.78%
}

BOX_NUMBERS = {4, 5, 6, 8, 9, 10}

# Skill level thresholds
SKILL_LEVELS = {
    "beginner": 0,
    "intermediate": 500,
    "advanced": 1500,
    "expert": 3000,
}


# ---------------------------------------------
# GET /api/sessions/<id>/analytics — Full post-session analytics
# Item #30
# ---------------------------------------------
@app.route('/api/sessions/<int:session_id>/analytics', methods=['GET'])
@login_required
def session_analytics(session_id):
    """
    Full analytics package for a session.

    Query params:
      fatigue_window — roll window size for fatigue curve (default 20)
      sig_threshold  — % deviation to flag signature numbers (default 15)

    Returns:
      - Core metrics (SRR, BSR, axis control)
      - Number distribution with hot/cold flags
      - Fatigue curve (SRR by rolling window)
      - Rotation summary (if face data exists)
      - Per-hand breakdown (play mode)
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

        fatigue_window = request.args.get("fatigue_window", 20, type=int)
        sig_threshold = request.args.get("sig_threshold", 15, type=float)

        rolls = Roll.query.filter_by(session_id=session.id).order_by(Roll.roll_number.asc()).all()
        total_rolls = len(rolls)

        if total_rolls == 0:
            return jsonify({"error": "No rolls in this session"}), 404

        # ── Core Metrics ─────────────────────────────────────
        totals = [r.total for r in rolls]
        sevens = sum(1 for t in totals if t == 7)
        box_count = sum(1 for t in totals if t in BOX_NUMBERS)

        srr = round(total_rolls / sevens, 2) if sevens > 0 else None
        bsr = round(box_count / sevens, 2) if sevens > 0 else None
        axis_pct = round(((session.total_on_axis or 0) / total_rolls) * 100, 1) if total_rolls > 0 else None
        doubles_pct = round(((session.total_doubles or 0) / total_rolls) * 100, 1) if total_rolls > 0 else None

        # ── Number Distribution + Signature Numbers ──────────
        dist = session.number_distribution or {}
        signature_numbers = []
        for num in range(2, 13):
            count = dist.get(str(num), 0)
            actual_pct = (count / total_rolls * 100) if total_rolls > 0 else 0
            expected_pct = RANDOM_DISTRIBUTION[num] * 100
            deviation = actual_pct - expected_pct
            deviation_pct = round((deviation / expected_pct) * 100, 1) if expected_pct > 0 else 0

            entry = {
                "number": num,
                "count": count,
                "actual_pct": round(actual_pct, 1),
                "expected_pct": round(expected_pct, 2),
                "deviation_pct": deviation_pct,
            }

            # Flag hot/cold based on configurable threshold
            if abs(deviation_pct) >= sig_threshold:
                entry["flag"] = "hot" if deviation_pct > 0 else "cold"

            signature_numbers.append(entry)

        # ── Fatigue Curve ────────────────────────────────────
        fatigue_curve = []
        if total_rolls >= fatigue_window:
            for start in range(0, total_rolls - fatigue_window + 1, fatigue_window):
                window = totals[start:start + fatigue_window]
                window_sevens = sum(1 for t in window if t == 7)
                window_srr = round(len(window) / window_sevens, 2) if window_sevens > 0 else None
                fatigue_curve.append({
                    "window_start": start + 1,
                    "window_end": start + len(window),
                    "rolls": len(window),
                    "sevens": window_sevens,
                    "srr": window_srr,
                })

        # ── Fatigue Warning ──────────────────────────────────
        fatigue_warning = None
        if len(fatigue_curve) >= 2 and fatigue_curve[0]["srr"] and fatigue_curve[-1]["srr"]:
            first_srr = fatigue_curve[0]["srr"]
            last_srr = fatigue_curve[-1]["srr"]
            if last_srr < first_srr * 0.7:
                fatigue_warning = {
                    "detected": True,
                    "first_window_srr": first_srr,
                    "last_window_srr": last_srr,
                    "decline_pct": round((1 - last_srr / first_srr) * 100, 1),
                    "message": (
                        f"Your SRR dropped from {first_srr} to {last_srr} over "
                        f"this session — a {round((1 - last_srr / first_srr) * 100, 1)}% "
                        f"decline. Your mechanics may be fatiguing."
                    ),
                }

        # ── Rotation Summary (if face data exists) ───────────
        rotation_summary = None
        rotation_rolls = [r for r in rolls if r.left_x_rotation is not None]
        if rotation_rolls:
            left_x_vals = [r.left_x_rotation for r in rotation_rolls]
            left_y_vals = [r.left_y_rotation for r in rotation_rolls if r.left_y_rotation is not None]
            left_z_vals = [r.left_z_rotation for r in rotation_rolls if r.left_z_rotation is not None]
            right_x_vals = [r.right_x_rotation for r in rotation_rolls if r.right_x_rotation is not None]
            right_y_vals = [r.right_y_rotation for r in rotation_rolls if r.right_y_rotation is not None]
            right_z_vals = [r.right_z_rotation for r in rotation_rolls if r.right_z_rotation is not None]

            def avg(vals):
                return round(sum(vals) / len(vals), 2) if vals else None

            rotation_summary = {
                "throws_with_face_data": len(rotation_rolls),
                "left_die": {
                    "avg_x": avg(left_x_vals),
                    "avg_y": avg(left_y_vals),
                    "avg_z": avg(left_z_vals),
                },
                "right_die": {
                    "avg_x": avg(right_x_vals),
                    "avg_y": avg(right_y_vals),
                    "avg_z": avg(right_z_vals),
                },
            }

        # ── Response ─────────────────────────────────────────
        return jsonify({
            "session_id": session.id,
            "total_rolls": total_rolls,
            "core_metrics": {
                "srr": srr,
                "bsr": bsr,
                "axis_control_pct": axis_pct,
                "doubles_pct": doubles_pct,
                "total_sevens": sevens,
                "total_box_numbers": box_count,
                "longest_hand": session.longest_hand,
                "avg_hand_length": session.avg_hand_length,
            },
            "signature_numbers": signature_numbers,
            "fatigue_curve": fatigue_curve,
            "fatigue_warning": fatigue_warning,
            "rotation_summary": rotation_summary,
            "config": {
                "fatigue_window": fatigue_window,
                "sig_threshold": sig_threshold,
            },
        }), 200

    except Exception as e:
        app.logger.error(f"Session analytics error: {str(e)}")
        return jsonify({"error": "Failed to compute analytics"}), 500


# ---------------------------------------------
# GET /api/users/me/signature — Current shooter signature
# Item #31
# ---------------------------------------------
@app.route('/api/users/me/signature', methods=['GET'])
@login_required
def get_my_signature():
    """
    Returns the current shooter signature including:
    - Modal rotations per die per axis
    - Consistency scores
    - Axis control rating
    - Confidence score
    - Set recommendation with reason
    - Signature history for trend analysis
    """
    try:
        user = get_current_user()
        if not user:
            return jsonify({"error": "User not found"}), 404

        sig = ShooterSignature.query.filter_by(user_id=user.id).first()
        if not sig or sig.total_throws_analyzed == 0:
            return jsonify({
                "status": "no_signature",
                "message": "No signature data yet. Complete a session with face capture data to build your signature.",
            }), 200

        # Get recommended set details
        rec_set = None
        if sig.recommended_set_id:
            ds = DiceSet.query.get(sig.recommended_set_id)
            if ds:
                rec_set = ds.to_dict()

        # Get signature history (last 20 snapshots for trend)
        history = (
            SignatureHistory.query
            .filter_by(user_id=user.id)
            .order_by(SignatureHistory.created_at.desc())
            .limit(20)
            .all()
        )

        return jsonify({
            "status": "ok",
            "signature": sig.to_dict(),
            "recommended_set": rec_set,
            "history": [h.to_dict() for h in history],
        }), 200

    except Exception as e:
        app.logger.error(f"Get signature error: {str(e)}")
        return jsonify({"error": "Failed to get signature"}), 500


# ---------------------------------------------
# GET /api/users/me/stats — Lifetime aggregate stats
# Item #32
# ---------------------------------------------
@app.route('/api/users/me/stats', methods=['GET'])
@login_required
def get_my_stats():
    """
    Returns lifetime aggregate statistics from UserStats.
    Includes number distribution for bet strategy engine.

    Query params:
      sig_threshold — % deviation to flag lifetime signature numbers (default 15)
    """
    try:
        user = get_current_user()
        if not user:
            return jsonify({"error": "User not found"}), 404

        stats = UserStats.query.filter_by(user_id=user.id).first()
        if not stats:
            return jsonify({"error": "No stats found"}), 404

        sig_threshold = request.args.get("sig_threshold", 15, type=float)

        # Compute lifetime signature numbers with hot/cold flags
        lifetime_dist = stats.lifetime_number_distribution or {}
        total = stats.lifetime_rolls or 0
        lifetime_signature = []

        for num in range(2, 13):
            count = lifetime_dist.get(str(num), 0)
            actual_pct = (count / total * 100) if total > 0 else 0
            expected_pct = RANDOM_DISTRIBUTION[num] * 100
            deviation = actual_pct - expected_pct
            deviation_pct = round((deviation / expected_pct) * 100, 1) if expected_pct > 0 else 0

            entry = {
                "number": num,
                "count": count,
                "actual_pct": round(actual_pct, 1),
                "expected_pct": round(expected_pct, 2),
                "deviation_pct": deviation_pct,
            }
            if abs(deviation_pct) >= sig_threshold:
                entry["flag"] = "hot" if deviation_pct > 0 else "cold"
            lifetime_signature.append(entry)

        return jsonify({
            "stats": stats.to_dict(),
            "lifetime_signature_numbers": lifetime_signature,
        }), 200

    except Exception as e:
        app.logger.error(f"Get stats error: {str(e)}")
        return jsonify({"error": "Failed to get stats"}), 500


# ---------------------------------------------
# GET /api/users/me/progress — Skill progression + milestones
# Item #33
# ---------------------------------------------
@app.route('/api/users/me/progress', methods=['GET'])
@login_required
def get_my_progress():
    """
    Returns skill progression data:
    - Current skill level and points
    - Milestones earned
    - Next level requirements
    - What unlocks at next level
    """
    try:
        user = get_current_user()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Current level info
        current_points = user.skill_points or 0
        current_level = user.skill_level or "beginner"

        # Find next level
        levels_ordered = ["beginner", "intermediate", "advanced", "expert"]
        current_idx = levels_ordered.index(current_level) if current_level in levels_ordered else 0
        next_level = levels_ordered[current_idx + 1] if current_idx < len(levels_ordered) - 1 else None
        next_level_points = SKILL_LEVELS.get(next_level) if next_level else None
        points_to_next = (next_level_points - current_points) if next_level_points else 0

        # What unlocks at next level
        unlocks = {
            "intermediate": [
                "3-V and 2-V dice sets",
                "Full X/Y/Z rotation analysis",
                "Intermediate training lessons",
                "Set recommendation (Quick View)",
            ],
            "advanced": [
                "Custom dice sets",
                "Full rotation/transpose analysis",
                "Advanced training lessons",
                "Set recommendation (Deep Dive)",
                "Signature history trends",
            ],
            "expert": [
                "All features unlocked",
                "Community leaderboards",
                "Create and share custom sets",
                "Multi-set recommendation comparison",
            ],
        }

        # Earned milestones
        milestones = (
            SkillProgression.query
            .filter_by(user_id=user.id)
            .order_by(SkillProgression.achieved_at.desc())
            .all()
        )

        milestones_data = [{
            "id": m.id,
            "milestone_type": m.milestone_type,
            "milestone_value": m.milestone_value,
            "points_awarded": m.points_awarded,
            "achieved_at": m.achieved_at.isoformat() if m.achieved_at else None,
        } for m in milestones]

        return jsonify({
            "current_level": current_level,
            "current_points": current_points,
            "next_level": next_level,
            "points_to_next_level": max(0, points_to_next),
            "next_level_points_required": next_level_points,
            "progress_pct": round((current_points / next_level_points) * 100, 1) if next_level_points else 100.0,
            "next_level_unlocks": unlocks.get(next_level, []),
            "milestones_earned": milestones_data,
            "total_milestones": len(milestones_data),
        }), 200

    except Exception as e:
        app.logger.error(f"Get progress error: {str(e)}")
        return jsonify({"error": "Failed to get progress"}), 500
