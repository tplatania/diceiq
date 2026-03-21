# ===============================
# Signature Service
# Computes a shooter's rotation signature from their roll history
#
# What this does:
#   1. Pulls all rolls with face/rotation data for the user
#   2. Filters to the current mechanic era only
#   3. Finds modal (most common) X/Y/Z value per die
#   4. Computes consistency score per axis per die
#   5. Rates axis control: poor / developing / controlled / elite
#   6. Computes confidence score 0-100
#   7. Recommends the best dice set for their natural throw
#   8. Detects mechanic drift and flags for era prompt
#
# Physics reference: DiceIQ Physics & Coaching Language Bible v1.1
#   X = pitch (backspin) — evaluated for consistency, not magnitude
#   Y = yaw (helicopter) — evaluated for nearness to zero
#   Z = roll (sideways tilt) — evaluated for nearness to zero
#
# FIXES APPLIED (code review March 2026):
#   - reset_era() no longer passes non-existent fields to SignatureHistory
#   - reset_era() uses snapshot_type='manual_reset', session_id=None
#   - compute_signature() now correctly counts and saves sessions_analyzed
# ===============================

from collections import Counter
from datetime import datetime, timezone
from sqlalchemy import func
from backend.config import db
from backend.models.roll import Roll
from backend.models.session import Session
from backend.models.shooter_signature import ShooterSignature
from backend.models.signature_history import SignatureHistory
from backend.models.dice_set import DiceSet
from backend.services.dice_orientation import rank_sets_for_signature


# ── Thresholds ────────────────────────────────────────────────────────────────

# Minimum throws before any signature or recommendation is issued
MIN_THROWS_FOR_SIGNATURE = 20

# Drift detection: if Y or Z average shifts by this much
# across the last 3 sessions vs the prior baseline, flag it
DRIFT_THRESHOLD = 1.5

# How many recent sessions to compare vs baseline for drift
DRIFT_WINDOW = 3


# ── Confidence Score ──────────────────────────────────────────────────────────

def compute_confidence(throw_count, avg_y_consistency, avg_z_consistency, avg_x_consistency):
    """
    Confidence score 0-100.
    Based on sample size (primary) and consistency (secondary).

    Tier mapping (from Physics Bible):
      0-19   = no recommendation
      20-39  = preliminary
      40-59  = working
      60-79  = reliable
      80-100 = high confidence / face control coaching unlocked
    """
    if throw_count < MIN_THROWS_FOR_SIGNATURE:
        return 0.0

    # Sample size score (max 60 points)
    if throw_count >= 200:
        size_score = 60.0
    elif throw_count >= 100:
        size_score = 45.0 + (throw_count - 100) / 100 * 15.0
    elif throw_count >= 50:
        size_score = 30.0 + (throw_count - 50) / 50 * 15.0
    else:
        # 20-49 throws: 10-30 points
        size_score = 10.0 + (throw_count - 20) / 30 * 20.0

    # Consistency score (max 40 points)
    # Y and Z nearness to zero is the primary goal
    # X consistency is secondary (reward repeatable backspin)
    yz_consistency = (avg_y_consistency + avg_z_consistency) / 2
    consistency_score = (yz_consistency * 24) + (avg_x_consistency * 16)

    return min(100.0, round(size_score + consistency_score, 1))


# ── Axis Control Rating ───────────────────────────────────────────────────────

def compute_axis_control_rating(avg_y, avg_z, y_consistency, z_consistency):
    """
    Rates overall axis control based on Y and Z behaviour.
    Y and Z near zero = good axis control.

    elite:      both axes average < 0.5, consistency > 80%
    controlled: both axes average < 1.0, consistency > 60%
    developing: both axes average < 2.0
    poor:       either axis average >= 2.0
    """
    y_abs = abs(avg_y) if avg_y is not None else 99
    z_abs = abs(avg_z) if avg_z is not None else 99
    yz_consistency = (y_consistency + z_consistency) / 2

    if y_abs < 0.5 and z_abs < 0.5 and yz_consistency >= 0.80:
        return "elite"
    elif y_abs < 1.0 and z_abs < 1.0 and yz_consistency >= 0.60:
        return "controlled"
    elif y_abs < 2.0 and z_abs < 2.0:
        return "developing"
    else:
        return "poor"


# ── Modal + Consistency ───────────────────────────────────────────────────────

def compute_modal_and_consistency(values):
    """
    Given a list of integer rotation values, returns:
      - modal value (most common)
      - consistency (fraction of values that match modal)
      - average (mean value)

    Returns (None, 0.0, 0.0) if list is empty.
    """
    if not values:
        return None, 0.0, 0.0

    counter = Counter(values)
    modal_value, modal_count = counter.most_common(1)[0]
    consistency = modal_count / len(values)
    average = sum(values) / len(values)

    return modal_value, round(consistency, 3), round(average, 3)


# ── Set Recommendation ────────────────────────────────────────────────────────

def recommend_set(modal_y, modal_z, target="srr"):
    """
    Recommend the best built-in dice set given the shooter's axis state and target.

    Logic:
      - Y and Z both near zero → axis control confirmed → match by target goal
      - Y or Z elevated        → axis control developing → Hard Way regardless
        (Hard Way is most forgiving — seven avoidance without face control)

    target options: srr / 6_8 / 5_9 / 4_10 / all_box / come_out

    Returns dict: { set_name, reason, confidence_note }
    """
    y_clean = abs(modal_y or 0) < 1
    z_clean = abs(modal_z or 0) < 1

    # Axis not yet clean — protect first, optimise later
    if not y_clean or not z_clean:
        return {
            "set_name": "Hard Way",
            "reason": (
                "Your Y or Z rotation is not yet near zero, which means "
                "axis control is still developing. The Hard Way set is the "
                "most forgiving set for a developing throw — it provides "
                "seven protection without requiring precise face control. "
                "Focus on suppressing your Y and Z deviation before "
                "optimising for a target number."
            ),
            "confidence_note": "Set recommendation will refine as axis control improves.",
        }

    # Axis clean — match by betting goal
    goal_map = {
        "come_out": {
            "set_name": "All Sevens",
            "reason": (
                "Your axis control is clean. For the come-out roll, "
                "All Sevens maximises 7s on axis — 4 out of 16 "
                "combinations produce a natural winner."
            ),
        },
        "6_8": {
            "set_name": "3V Hard Six",
            "reason": (
                "Your axis control is clean. For 6 and 8 targeting, "
                "the 3V Hard Six produces 3 sixes and 3 eights on axis "
                "— 6 target hits out of 16 — with only 2 sevens. "
                "Best seven protection of any six-and-eight set at 12 percent."
            ),
        },
        "5_9": {
            "set_name": "Mini-V Hard 4",
            "reason": (
                "Your axis control is clean. For 5 and 9 targeting, "
                "the Mini-V Hard 4 produces 2 fives and 2 nines on axis "
                "with strong 6 and 8 coverage as a bonus."
            ),
        },
        "4_10": {
            "set_name": "2V Set",
            "reason": (
                "Your axis control is clean. For 4 and 10 targeting, "
                "the 2V Set produces 2 fours and 2 tens on axis "
                "with only 2 sevens — 12 percent seven rate. "
                "Best protection for outside number players."
            ),
        },
        "all_box": {
            "set_name": "Crossed Sixes",
            "reason": (
                "Your axis control is clean. For all box numbers, "
                "Crossed Sixes is the strongest set — 10 box number "
                "hits out of 16 with only 2 sevens on axis. "
                "62 percent target rate, 12 percent seven rate. "
                "The best all-around set for shooters with bets across the board."
            ),
        },
        "srr": {
            "set_name": "Hard Way",
            "reason": (
                "Your axis control is clean. For maximising SRR and "
                "general seven avoidance, the Hard Way set provides "
                "solid protection with 4 sevens on axis out of 16. "
                "Simple to set, consistent muscle memory."
            ),
        },
    }

    # Copy to avoid mutating the local dict definition
    result = dict(goal_map.get(target, goal_map["srr"]))
    result["confidence_note"] = "Axis control confirmed. Recommendation based on your target goal."
    return result


# ── Drift Detection ───────────────────────────────────────────────────────────

def detect_drift(user_id, current_era_start):
    """
    Compare Y and Z averages over the last DRIFT_WINDOW sessions
    vs the baseline for the current era.

    Returns dict: { drift_detected, y_baseline, y_recent, z_baseline, z_recent }
    """
    sessions = (
        Session.query
        .filter_by(user_id=user_id)
        .filter(Session.started_at >= current_era_start)
        .order_by(Session.started_at.asc())
        .all()
    )

    if len(sessions) < DRIFT_WINDOW + 2:
        return {"drift_detected": False}

    session_ids = [s.id for s in sessions]

    def get_yz_averages(sids):
        rolls = Roll.query.filter(
            Roll.session_id.in_(sids),
            Roll.left_y_rotation.isnot(None),
        ).all()
        if not rolls:
            return None, None
        y_vals = [r.left_y_rotation for r in rolls if r.left_y_rotation is not None]
        z_vals = [r.left_z_rotation for r in rolls if r.left_z_rotation is not None]
        avg_y = sum(y_vals) / len(y_vals) if y_vals else None
        avg_z = sum(z_vals) / len(z_vals) if z_vals else None
        return avg_y, avg_z

    baseline_ids = session_ids[:-DRIFT_WINDOW]
    recent_ids   = session_ids[-DRIFT_WINDOW:]

    baseline_y, baseline_z = get_yz_averages(baseline_ids)
    recent_y,   recent_z   = get_yz_averages(recent_ids)

    if baseline_y is None or recent_y is None:
        return {"drift_detected": False}

    y_shift = abs(recent_y - baseline_y)
    z_shift = abs(recent_z - baseline_z) if baseline_z is not None and recent_z is not None else 0

    drift = y_shift >= DRIFT_THRESHOLD or z_shift >= DRIFT_THRESHOLD

    return {
        "drift_detected":     drift,
        "y_baseline":         round(baseline_y, 2),
        "y_recent":           round(recent_y, 2),
        "z_baseline":         round(baseline_z, 2) if baseline_z is not None else None,
        "z_recent":           round(recent_z, 2)   if recent_z   is not None else None,
        "y_shift":            round(y_shift, 2),
        "z_shift":            round(z_shift, 2),
        "sessions_in_window": DRIFT_WINDOW,
    }


# ── Main Compute Function ─────────────────────────────────────────────────────

def compute_signature(user_id, target="srr", era_start=None):
    """
    Main entry point. Computes the full shooter signature for a user.

    Steps:
      1. Pull all rolls with rotation data in current era
      2. Count distinct sessions contributing to signature
      3. Compute modal X/Y/Z and consistency per die
      4. Rate axis control
      5. Compute confidence score
      6. Recommend best set for target
      7. Save to ShooterSignature table
      8. Check for mechanic drift
      9. Return full result dict

    Args:
      user_id   — the user to compute for
      target    — betting goal: srr / 6_8 / 5_9 / 4_10 / all_box / come_out
      era_start — datetime of current era start, or None for all-time

    Returns dict with full signature data and any drift warning.
    """

    # ── Step 1: Pull qualifying rolls ──────────────────────────────────────
    query = (
        db.session.query(Roll)
        .join(Session, Roll.session_id == Session.id)
        .filter(Session.user_id == user_id)
        .filter(Roll.left_x_rotation.isnot(None))   # only throws with face data
    )

    if era_start:
        query = query.filter(Session.started_at >= era_start)

    rolls = query.all()
    throw_count = len(rolls)

    # Not enough data yet — return early with a coaching message
    if throw_count < MIN_THROWS_FOR_SIGNATURE:
        return {
            "status":        "insufficient_data",
            "throw_count":   throw_count,
            "throws_needed": MIN_THROWS_FOR_SIGNATURE - throw_count,
            "message": (
                f"I need at least {MIN_THROWS_FOR_SIGNATURE} throws with face data "
                f"to build your signature. "
                f"You have {throw_count} — "
                f"{MIN_THROWS_FOR_SIGNATURE - throw_count} more to go."
            ),
        }

    # ── Step 2: Count distinct sessions ───────────────────────────────────
    # FIX: sessions_analyzed was never being set — now computed properly
    session_count_query = (
        db.session.query(func.count(func.distinct(Roll.session_id)))
        .join(Session, Roll.session_id == Session.id)
        .filter(Session.user_id == user_id)
        .filter(Roll.left_x_rotation.isnot(None))
    )
    if era_start:
        session_count_query = session_count_query.filter(Session.started_at >= era_start)
    sessions_analyzed = session_count_query.scalar() or 0

    # ── Step 3: Extract rotation lists per axis per die ───────────────────
    lx = [r.left_x_rotation  for r in rolls if r.left_x_rotation  is not None]
    ly = [r.left_y_rotation   for r in rolls if r.left_y_rotation  is not None]
    lz = [r.left_z_rotation   for r in rolls if r.left_z_rotation  is not None]
    rx = [r.right_x_rotation  for r in rolls if r.right_x_rotation is not None]
    ry = [r.right_y_rotation  for r in rolls if r.right_y_rotation is not None]
    rz = [r.right_z_rotation  for r in rolls if r.right_z_rotation is not None]

    # ── Step 4: Modal + Consistency per axis per die ───────────────────────
    left_modal_x,  left_x_con,  left_x_avg  = compute_modal_and_consistency(lx)
    left_modal_y,  left_y_con,  left_y_avg  = compute_modal_and_consistency(ly)
    left_modal_z,  left_z_con,  left_z_avg  = compute_modal_and_consistency(lz)
    right_modal_x, right_x_con, right_x_avg = compute_modal_and_consistency(rx)
    right_modal_y, right_y_con, right_y_avg = compute_modal_and_consistency(ry)
    right_modal_z, right_z_con, right_z_avg = compute_modal_and_consistency(rz)

    # Cross-die averages for rating and confidence
    avg_y_con = (left_y_con + right_y_con) / 2
    avg_z_con = (left_z_con + right_z_con) / 2
    avg_x_con = (left_x_con + right_x_con) / 2
    avg_y_avg = (left_y_avg + right_y_avg) / 2
    avg_z_avg = (left_z_avg + right_z_avg) / 2

    # ── Step 5: Axis control rating ────────────────────────────────────────
    rating = compute_axis_control_rating(avg_y_avg, avg_z_avg, avg_y_con, avg_z_con)

    # ── Step 6: Confidence score ───────────────────────────────────────────
    confidence = compute_confidence(throw_count, avg_y_con, avg_z_con, avg_x_con)

    # ── Step 7: Set recommendation (576 Matrix ranking engine) ─────────────
    # Ranks ALL preset sets by applying the shooter's actual rotation
    # signature to each set and computing resulting on-axis distributions.
    # Returns a ranked list, not just one pick — shooter can try alternatives.
    ranked_sets = rank_sets_for_signature(
        left_modal_x, left_modal_y, left_modal_z,
        right_modal_x, right_modal_y, right_modal_z,
        target=target,
    )

    # Top pick for saving to the signature record
    top_pick = ranked_sets[0] if ranked_sets else None
    rec_set_id = None
    if top_pick:
        rec_set = DiceSet.query.filter_by(name=top_pick["name"], set_type="builtin").first()
        rec_set_id = rec_set.id if rec_set else None

    # ── Step 8: Save to ShooterSignature ──────────────────────────────────
    sig = ShooterSignature.query.filter_by(user_id=user_id).first()
    if not sig:
        sig = ShooterSignature(user_id=user_id)
        db.session.add(sig)

    sig.sessions_analyzed     = sessions_analyzed   # FIX: was never being set
    sig.total_throws_analyzed = throw_count
    sig.left_modal_x          = left_modal_x
    sig.left_modal_y          = left_modal_y
    sig.left_modal_z          = left_modal_z
    sig.left_x_consistency    = left_x_con
    sig.left_y_consistency    = left_y_con
    sig.left_z_consistency    = left_z_con
    sig.right_modal_x         = right_modal_x
    sig.right_modal_y         = right_modal_y
    sig.right_modal_z         = right_modal_z
    sig.right_x_consistency   = right_x_con
    sig.right_y_consistency   = right_y_con
    sig.right_z_consistency   = right_z_con
    sig.axis_control_rating   = rating
    sig.signature_confidence  = confidence
    sig.recommended_set_id    = rec_set_id
    sig.recommendation_reason = top_pick["name"] + ": Score " + str(top_pick["score"]) if top_pick else None
    sig.recommendation_target = target
    sig.last_computed_at      = datetime.now(timezone.utc).replace(tzinfo=None)
    sig.needs_recompute       = False

    db.session.commit()

    # ── Step 9: Drift check ────────────────────────────────────────────────
    drift = {"drift_detected": False}
    if era_start:
        drift = detect_drift(user_id, era_start)

    # ── Return full result ─────────────────────────────────────────────────
    return {
        "status":              "ok",
        "throw_count":         throw_count,
        "sessions_analyzed":   sessions_analyzed,
        "confidence":          confidence,
        "axis_control_rating": rating,

        "left_die": {
            "modal_x":       left_modal_x,
            "modal_y":       left_modal_y,
            "modal_z":       left_modal_z,
            "x_consistency": left_x_con,
            "y_consistency": left_y_con,
            "z_consistency": left_z_con,
            "x_avg":         left_x_avg,
            "y_avg":         left_y_avg,
            "z_avg":         left_z_avg,
        },
        "right_die": {
            "modal_x":       right_modal_x,
            "modal_y":       right_modal_y,
            "modal_z":       right_modal_z,
            "x_consistency": right_x_con,
            "y_consistency": right_y_con,
            "z_consistency": right_z_con,
            "x_avg":         right_x_avg,
            "y_avg":         right_y_avg,
            "z_avg":         right_z_avg,
        },

        "recommendation": {
            "ranked_sets":     ranked_sets,
            "top_pick":        top_pick["name"] if top_pick else None,
            "top_score":       top_pick["score"] if top_pick else None,
            "target":          target,
        },

        "drift": drift,
    }


# ── Era Reset ─────────────────────────────────────────────────────────────────

def reset_era(user_id):
    """
    Archives the current ShooterSignature as a SignatureHistory snapshot,
    then clears ShooterSignature so a fresh era begins on the next throw.

    Called when:
      - Shooter manually taps 'Start New Baseline'
      - Shooter confirms AI drift detection prompt

    FIX: No longer passes non-existent fields (recommendation_reason, era_end).
    FIX: session_id=None is valid — SignatureHistory.session_id is now nullable.
    FIX: snapshot_type='manual_reset' distinguishes era resets from session snapshots.

    Returns dict with status and archived snapshot id.
    """
    sig = ShooterSignature.query.filter_by(user_id=user_id).first()
    if not sig or sig.total_throws_analyzed == 0:
        return {"status": "nothing_to_archive"}

    # Archive current era as a named snapshot
    snapshot = SignatureHistory(
        user_id               = user_id,
        session_id            = None,                    # FIX: no session for manual reset
        snapshot_type         = "manual_reset",          # FIX: distinguish from session snapshots
        sessions_analyzed     = sig.sessions_analyzed or 0,
        total_throws_analyzed = sig.total_throws_analyzed,
        left_modal_x          = sig.left_modal_x,
        left_modal_y          = sig.left_modal_y,
        left_modal_z          = sig.left_modal_z,
        left_x_consistency    = sig.left_x_consistency,
        left_y_consistency    = sig.left_y_consistency,
        left_z_consistency    = sig.left_z_consistency,
        right_modal_x         = sig.right_modal_x,
        right_modal_y         = sig.right_modal_y,
        right_modal_z         = sig.right_modal_z,
        right_x_consistency   = sig.right_x_consistency,
        right_y_consistency   = sig.right_y_consistency,
        right_z_consistency   = sig.right_z_consistency,
        axis_control_rating   = sig.axis_control_rating,
        signature_confidence  = sig.signature_confidence,
        recommended_set_id    = sig.recommended_set_id,
        recommendation_target = sig.recommendation_target,  # FIX: correct field name
    )
    db.session.add(snapshot)

    # Wipe current signature — fresh era starts on next throw
    sig.sessions_analyzed     = 0
    sig.total_throws_analyzed = 0
    sig.left_modal_x          = None
    sig.left_modal_y          = None
    sig.left_modal_z          = None
    sig.left_x_consistency    = None
    sig.left_y_consistency    = None
    sig.left_z_consistency    = None
    sig.right_modal_x         = None
    sig.right_modal_y         = None
    sig.right_modal_z         = None
    sig.right_x_consistency   = None
    sig.right_y_consistency   = None
    sig.right_z_consistency   = None
    sig.axis_control_rating   = None
    sig.signature_confidence  = 0.0
    sig.recommendation_reason = None
    sig.last_computed_at      = None
    sig.needs_recompute       = False

    db.session.commit()

    return {
        "status":      "era_reset",
        "archived_id": snapshot.id,
        "message":     (
            "Your previous throw history has been archived. "
            "Starting fresh baseline now."
        ),
    }
