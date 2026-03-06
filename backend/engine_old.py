
# ─────────────────────────────────────────────────────────────
# DIAGNOSTIC ENGINE
# The "Mechanical Audit" layer
# Watches for fatigue, axis drift, SRR drops
# Returns messages that get whispered into Tom's hearing aids
# ─────────────────────────────────────────────────────────────

def run_diagnostics(session, current_roll_number):
    """
    Called after every roll. Returns a diagnostic alert if something
    needs Tom's attention, otherwise returns None.

    Checks (in priority order):
    1. Seven-out spike (3 sevens in last 10 rolls)
    2. Fatigue threshold (every 40 rolls)
    3. SRR drop warning
    4. Axis control drop
    5. Signature number emerging (positive feedback)
    """
    rolls = session.rolls
    if len(rolls) < 10:
        return None  # Not enough data yet

    alerts = []

    # --- 1. SEVEN SPIKE — most urgent ---
    last_10       = rolls[-10:]
    recent_sevens = sum(1 for r in last_10 if r.total == 7)
    if recent_sevens >= 3:
        alerts.append({
            "level":    "alert",
            "category": "seven_spike",
            "message":  "Three sevens in last ten rolls — check your set"
        })

    # --- 2. FATIGUE THRESHOLD ---
    if current_roll_number % FATIGUE_THRESHOLD == 0:
        alerts.append({
            "level":    "warning",
            "category": "fatigue",
            "message":  f"{current_roll_number} rolls — fatigue window, consider a break"
        })

    # --- 3. SRR DROP ---
    srr = calculate_srr(rolls)
    if srr and srr < SRR_WARNING_THRESHOLD:
        alerts.append({
            "level":    "warning",
            "category": "srr",
            "message":  f"SRR at {srr} — below target, stay focused"
        })

    # --- 4. AXIS CONTROL DROP ---
    axis_pct = calculate_axis_control(rolls)
    if axis_pct < AXIS_WARNING_THRESHOLD and len(rolls) >= 20:
        alerts.append({
            "level":    "warning",
            "category": "axis",
            "message":  f"Axis control at {axis_pct}% — check finger pressure"
        })

    # --- 5. SIGNATURE NUMBER (positive) ---
    if len(rolls) >= 30:
        signatures = calculate_signature_numbers(rolls)
        if signatures:
            top = signatures[0]
            alerts.append({
                "level":    "info",
                "category": "signature",
                "message":  f"{top['number']} running hot — {top['deviation']}% above expected"
            })

    # Return highest priority alert only (don't overwhelm Tom)
    if alerts:
        priority_order = ["alert", "warning", "info"]
        for level in priority_order:
            for alert in alerts:
                if alert["level"] == level:
                    return alert

    return None


def log_diagnostic(session_id, roll_number, alert):
    """Saves diagnostic alert to the database"""
    if not alert:
        return
    entry = DiagnosticLog(
        session_id  = session_id,
        roll_number = roll_number,
        level       = alert["level"],
        category    = alert["category"],
        message     = alert["message"]
    )
    db.session.add(entry)
    db.session.commit()
