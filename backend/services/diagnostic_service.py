# ===============================
# Diagnostic Service
# Per-throw fault detection and NASA-level coaching messages
# Checklist items: #34-35
#
# Physics reference: DiceIQ Physics & Coaching Language Bible v1.1
#   Section 4.2: Y-Axis Fault Diagnostics (Yaw)
#   Section 4.3: Z-Axis Fault Diagnostics (Roll)
#   Section 4.4: X-Axis Consistency Diagnostics (Pitch)
#   Section 7: Voice Coach Language Standards
#
# Runs after every roll (or on demand) and generates:
#   - Per-throw rotation diagnostics
#   - Rolling window trend alerts (fatigue, seven spike, axis drop)
#   - Coaching messages at NASA-level specificity
# ===============================

from backend.config import db
from backend.models.roll import Roll
from backend.models.session import Session
from backend.models.diagnostic_log import DiagnosticLog

# ── Y-Axis (Yaw) Fault Table ─────────────────────────────────────────────────
# From Physics Bible Section 4.2
# Y rotation = helicopter spin. Should be zero.

Y_AXIS_FAULTS = {
    0: {
        "severity": "CLEAN",
        "message": (
            "Zero yaw detected. Your release is synchronized. "
            "Axis control confirmed on this throw."
        ),
    },
    1: {
        "severity": "MINOR",
        "message": (
            "Minor Y deviation of {value} detected. Marginal finger timing "
            "offset — borderline acceptable. Monitor over your next 10 throws."
        ),
    },
    2: {
        "severity": "MODERATE",
        "message": (
            "Y-axis deviation of {value} detected. One finger is dragging "
            "on release approximately 20-30 milliseconds late. "
            "Focus on pressing all three fingertips flat against the "
            "die face and releasing as a single unit."
        ),
    },
    3: {
        "severity": "SIGNIFICANT",
        "message": (
            "Y-axis deviation of {value} confirmed. Clear zero-torque "
            "failure — your dice are separating in flight with visible "
            "helicopter spin. Check your index finger release pressure. "
            "All fingers must leave the die at the exact same moment."
        ),
    },
    4: {
        "severity": "CRITICAL",
        "message": (
            "Critical Y-axis deviation of {value} or greater. Your dice "
            "are helicoptering severely and landing on corners. Axis "
            "control is lost. Stop and reset your grip. Press the dice "
            "together firmly, ensure zero gap, and focus entirely on a "
            "synchronized finger release."
        ),
    },
}

# ── Z-Axis (Roll) Fault Table ────────────────────────────────────────────────
# From Physics Bible Section 4.3
# Z rotation = sideways tilt. Should be zero.

Z_AXIS_FAULTS = {
    0: {
        "severity": "CLEAN",
        "message": (
            "Zero roll deviation. Your dice are travelling as a unified "
            "mass with no sideways separation."
        ),
    },
    1: {
        "severity": "MINOR",
        "message": (
            "Z deviation of {value} detected. Slight grip gap. Ensure "
            "dice faces are pressed perfectly flush before release."
        ),
    },
    2: {
        "severity": "MODERATE",
        "message": (
            "Z-axis deviation of {value}. Your dice are separating "
            "during flight. Grip pressure is uneven between your thumb "
            "and fingers. Squeeze the dice together more firmly before "
            "your release."
        ),
    },
    3: {
        "severity": "SIGNIFICANT",
        "message": (
            "Z-axis deviation of {value} confirmed. Your dice are "
            "separating mid-flight and landing independently. This "
            "cannot be fixed with a set change — you need to fix your "
            "grip. The dice must behave as a single fused rectangular "
            "mass from grip through release."
        ),
    },
    4: {
        "severity": "CRITICAL",
        "message": (
            "Critical Z-axis deviation. Your dice are fully independent "
            "in the air — two separate objects following two separate "
            "paths. All axis control is lost. Reset your grip completely. "
            "Press dice faces flush, zero gap, equal pressure on all "
            "contact points."
        ),
    },
}

# ── Alert Thresholds ─────────────────────────────────────────────────────────
# From Architecture Blueprint Section 7.2

SEVEN_SPIKE_THRESHOLD = 3      # 3+ sevens in last 10 rolls
FATIGUE_INTERVAL = 40           # Check every 40 rolls
SRR_DROP_THRESHOLD = 5.5       # Session SRR below this triggers alert
AXIS_DROP_THRESHOLD = 15.0     # Axis below 15% after 20+ rolls
DIE_OFF_AXIS_THRESHOLD = 5    # One die off-axis 5+ times in last 10
GREAT_HAND_THRESHOLD = 15     # 15+ rolls without a seven


# ── Helper: Get fault entry for an axis value ────────────────────────────────

def _get_fault(fault_table, value):
    """Look up the fault entry for a given rotation value."""
    abs_val = abs(value) if value is not None else 0
    # Clamp to max defined level (4+)
    key = min(abs_val, 4)
    entry = fault_table.get(key, fault_table[4])

    # Include direction info for coaching value
    if value is not None and value != 0:
        direction = "left" if value > 0 else "right"  # Y: +left -right, Z: +right -left
    else:
        direction = None

    return {
        "severity": entry["severity"],
        "message": entry["message"].format(value=abs_val),
        "value": value,
        "direction": direction,
    }


# ── Main Diagnostic Function ─────────────────────────────────────────────────

def diagnose_throw(session_id, roll_id=None):
    """
    Run diagnostics on the latest throw (or a specific roll) in a session.

    Generates:
    1. Per-throw rotation fault analysis (Y and Z axes)
    2. Rolling window trend alerts:
       - Seven spike (3+ sevens in last 10)
       - Fatigue warning (every 40 rolls)
       - SRR drop (below 5.5)
       - Axis control drop (below 15% after 20+ rolls)
       - Single die off-axis pattern
       - Great hand encouragement (15+ rolls)
    3. X-axis consistency feedback (periodic)

    Returns dict with diagnostics list and any alerts generated.
    Saves alerts to DiagnosticLog table.
    """
    session = Session.query.get(session_id)
    if not session:
        return {"error": "Session not found"}

    # Get the target roll
    if roll_id:
        roll = Roll.query.get(roll_id)
        if not roll:
            return {"error": "Roll not found"}
        if roll.session_id != session_id:
            return {"error": "Roll does not belong to this session"}
    else:
        roll = (Roll.query
                .filter_by(session_id=session_id)
                .order_by(Roll.roll_number.desc())
                .first())

    if not roll:
        return {"error": "No rolls in session"}

    diagnostics = []
    alerts = []

    # ── 1. Per-throw rotation diagnostics ────────────────────
    if roll.left_y_rotation is not None:
        left_y = _get_fault(Y_AXIS_FAULTS, roll.left_y_rotation)
        left_y["die"] = "left"
        left_y["axis"] = "Y"
        diagnostics.append(left_y)

    if roll.right_y_rotation is not None:
        right_y = _get_fault(Y_AXIS_FAULTS, roll.right_y_rotation)
        right_y["die"] = "right"
        right_y["axis"] = "Y"
        diagnostics.append(right_y)

    if roll.left_z_rotation is not None:
        left_z = _get_fault(Z_AXIS_FAULTS, roll.left_z_rotation)
        left_z["die"] = "left"
        left_z["axis"] = "Z"
        diagnostics.append(left_z)

    if roll.right_z_rotation is not None:
        right_z = _get_fault(Z_AXIS_FAULTS, roll.right_z_rotation)
        right_z["die"] = "right"
        right_z["axis"] = "Z"
        diagnostics.append(right_z)

    # ── 2. Rolling window trend alerts ───────────────────────

    # Get recent rolls for window analysis
    recent_rolls = (
        Roll.query
        .filter_by(session_id=session_id)
        .order_by(Roll.roll_number.desc())
        .limit(20)
        .all()
    )
    recent_rolls.reverse()  # oldest first

    total_rolls = session.total_rolls or 0
    roll_number = roll.roll_number

    # ── Seven Spike: 3+ sevens in last 10 rolls ──
    last_10 = recent_rolls[-10:] if len(recent_rolls) >= 10 else recent_rolls
    recent_sevens = sum(1 for r in last_10 if r.total == 7)
    if recent_sevens >= SEVEN_SPIKE_THRESHOLD:
        alert = {
            "category": "seven_spike",
            "level": "alert",
            "message": (
                f"Seven spike detected: {recent_sevens} sevens in your "
                f"last {len(last_10)} throws. Your SRR is dropping. "
                f"Check your release mechanics and grip pressure."
            ),
        }
        alerts.append(alert)

    # ── Fatigue Warning: every 40 rolls ──
    if roll_number > 0 and roll_number % FATIGUE_INTERVAL == 0:
        # Compare SRR of last 20 vs first 20
        if len(recent_rolls) >= 20:
            recent_window = recent_rolls[-20:]
            recent_sevens_w = sum(1 for r in recent_window if r.total == 7)
            recent_srr = len(recent_window) / recent_sevens_w if recent_sevens_w > 0 else 99

            first_20 = (
                Roll.query
                .filter_by(session_id=session_id)
                .order_by(Roll.roll_number.asc())
                .limit(20)
                .all()
            )
            first_sevens = sum(1 for r in first_20 if r.total == 7)
            first_srr = len(first_20) / first_sevens if first_sevens > 0 else 99

            if first_srr > 0 and recent_srr < first_srr * 0.7:
                alert = {
                    "category": "fatigue",
                    "level": "warning",
                    "message": (
                        f"Fatigue check at roll {total_rolls}. Your SRR "
                        f"has dropped from {round(first_srr, 1)} in your "
                        f"first 20 throws to {round(recent_srr, 1)} in your "
                        f"last 20. Your mechanics may be fatiguing. "
                        f"Consider taking a break."
                    ),
                }
                alerts.append(alert)

    # ── SRR Drop: session SRR below threshold ──
    session_srr = None
    if (session.total_sevens or 0) > 0 and total_rolls >= 20:
        session_srr = total_rolls / session.total_sevens
        if session_srr < SRR_DROP_THRESHOLD:
            alert = {
                "category": "srr_drop",
                "level": "warning",
                "message": (
                    f"Your session SRR is {round(session_srr, 2)} after "
                    f"{total_rolls} throws — below the {SRR_DROP_THRESHOLD} "
                    f"target. Focus on your release technique and consider "
                    f"whether fatigue is affecting your throw."
                ),
            }
            alerts.append(alert)

    # ── Axis Control Drop: below 15% after 20+ rolls ──
    if total_rolls >= 20 and session.total_on_axis is not None:
        axis_pct = ((session.total_on_axis or 0) / total_rolls) * 100
        if axis_pct < AXIS_DROP_THRESHOLD:
            alert = {
                "category": "axis_drop",
                "level": "warning",
                "message": (
                    f"Axis control is at {round(axis_pct, 1)}% after "
                    f"{total_rolls} throws — below the {AXIS_DROP_THRESHOLD}% "
                    f"baseline. Check your grip alignment and ensure the "
                    f"dice are set square before each throw."
                ),
            }
            alerts.append(alert)

    # ── Single Die Off-Axis Pattern ──
    if len(recent_rolls) >= 10:
        last_10_with_rot = [r for r in recent_rolls[-10:] if r.left_y_rotation is not None]
        if len(last_10_with_rot) >= 5:
            left_off = sum(1 for r in last_10_with_rot
                          if abs(r.left_y_rotation or 0) >= 2 or abs(r.left_z_rotation or 0) >= 2)
            right_off = sum(1 for r in last_10_with_rot
                           if abs(r.right_y_rotation or 0) >= 2 or abs(r.right_z_rotation or 0) >= 2)

            if left_off >= DIE_OFF_AXIS_THRESHOLD:
                alert = {
                    "category": "left_die_off_axis",
                    "level": "warning",
                    "message": (
                        f"Your left die has gone off-axis {left_off} times "
                        f"in your last {len(last_10_with_rot)} throws. This "
                        f"suggests a mechanical issue with your left hand "
                        f"grip or release. Focus on equal pressure across "
                        f"all fingertips on the left die."
                    ),
                }
                alerts.append(alert)

            if right_off >= DIE_OFF_AXIS_THRESHOLD:
                alert = {
                    "category": "right_die_off_axis",
                    "level": "warning",
                    "message": (
                        f"Your right die has gone off-axis {right_off} times "
                        f"in your last {len(last_10_with_rot)} throws. This "
                        f"suggests a mechanical issue with your right hand "
                        f"grip or release. Focus on equal pressure across "
                        f"all fingertips on the right die."
                    ),
                }
                alerts.append(alert)

    # ── Great Hand Encouragement ──
    if (session.current_hand_rolls or 0) >= GREAT_HAND_THRESHOLD:
        hand_rolls = session.current_hand_rolls
        if hand_rolls == GREAT_HAND_THRESHOLD:  # Only fire once at threshold
            alert = {
                "category": "great_hand",
                "level": "info",
                "message": (
                    f"Outstanding! {hand_rolls} rolls and counting without "
                    f"a seven. Your mechanics are locked in. "
                    f"Stay focused, stay consistent."
                ),
            }
            alerts.append(alert)

    # ── 3. X-Axis Consistency (periodic — every 20 throws) ───
    if roll_number > 0 and roll_number % 20 == 0:
        rolls_with_x = [r for r in recent_rolls if r.left_x_rotation is not None]
        if len(rolls_with_x) >= 10:
            from collections import Counter
            left_x_vals = [r.left_x_rotation for r in rolls_with_x]
            counter = Counter(left_x_vals)
            modal_val, modal_count = counter.most_common(1)[0]
            consistency = modal_count / len(left_x_vals)

            if consistency >= 0.80:
                x_msg = (
                    f"Your pitch axis is elite-level consistent. You are "
                    f"repeating X rotation of {modal_val} on "
                    f"{round(consistency * 100)}% of throws. This is face "
                    f"control territory."
                )
                x_level = "info"
            elif consistency >= 0.60:
                x_msg = (
                    f"Your pitch consistency is controlled at "
                    f"{round(consistency * 100)}%. Modal X rotation is "
                    f"{modal_val}. Keep your release point and arc consistent."
                )
                x_level = "info"
            elif consistency >= 0.40:
                x_msg = (
                    f"Your pitch axis is developing. X rotation varies — "
                    f"modal is {modal_val} at only {round(consistency * 100)}%. "
                    f"Focus on keeping your release point and arc the same "
                    f"on every throw."
                )
                x_level = "warning"
            else:
                x_msg = (
                    f"Your pitch axis shows high variance. Each throw "
                    f"produces a different backspin rate — modal X is "
                    f"{modal_val} at only {round(consistency * 100)}%. "
                    f"Your release point, arc, or energy is changing "
                    f"throw to throw. Simplify your mechanics."
                )
                x_level = "warning"

            alerts.append({
                "category": "x_consistency",
                "level": x_level,
                "message": x_msg,
            })

    # ── Save alerts to DiagnosticLog ─────────────────────────
    saved_alerts = []
    for alert in alerts:
        log = DiagnosticLog(
            session_id=session_id,
            roll_number=roll_number,
            level=alert["level"],
            category=alert["category"],
            message=alert["message"],
        )
        db.session.add(log)
        saved_alerts.append(log)

    if alerts:
        db.session.commit()

    # Serialize after commit so IDs and timestamps are populated
    saved_alerts_data = [log.to_dict() for log in saved_alerts]

    # ── Build response ───────────────────────────────────────
    # Find the worst severity in this throw's diagnostics
    worst = "CLEAN"
    severity_order = ["CLEAN", "MINOR", "MODERATE", "SIGNIFICANT", "CRITICAL"]
    for d in diagnostics:
        if severity_order.index(d["severity"]) > severity_order.index(worst):
            worst = d["severity"]

    return {
        "roll_number": roll_number,
        "total_rolls": total_rolls,
        "worst_severity": worst,
        "diagnostics": diagnostics,
        "alerts": saved_alerts_data,
        "alert_count": len(saved_alerts_data),
    }
