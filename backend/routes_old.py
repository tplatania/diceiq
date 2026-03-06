
# ─────────────────────────────────────────────────────────────
# ANALYTICS ENDPOINTS
# Called by the dashboard after the session
# ─────────────────────────────────────────────────────────────

@api.route('/session/<int:session_id>/analytics', methods=['GET'])
def get_analytics(session_id):
    """Full post-session analytics package"""
    session   = Session.query.get_or_404(session_id)
    analytics = full_session_analytics(session)
    return jsonify(analytics)


@api.route('/session/<int:session_id>/rolls', methods=['GET'])
def get_rolls(session_id):
    """Every roll in a session — for detailed review"""
    session = Session.query.get_or_404(session_id)
    return jsonify([r.to_dict() for r in session.rolls])


@api.route('/session/<int:session_id>/diagnostics', methods=['GET'])
def get_diagnostics(session_id):
    """All diagnostic alerts fired during a session"""
    logs = DiagnosticLog.query.filter_by(session_id=session_id)\
                              .order_by(DiagnosticLog.roll_number).all()
    return jsonify([l.to_dict() for l in logs])


@api.route('/lifetime', methods=['GET'])
def get_lifetime_stats():
    """
    Cruise-long performance summary.
    All sessions combined — the big picture.
    """
    sessions    = Session.query.all()
    all_rolls   = [r for s in sessions for r in s.rolls]
    all_hands   = [h for s in sessions for h in s.hands]

    total_rolls  = len(all_rolls)
    total_sevens = sum(1 for r in all_rolls if r.total == 7)
    total_doubles= sum(1 for r in all_rolls if r.is_double)

    lifetime_srr  = round(total_rolls / total_sevens, 2) if total_sevens > 0 else 0
    lifetime_axis = round((total_doubles / total_rolls) * 100, 1) if total_rolls > 0 else 0

    hand_lengths  = [h.roll_count() for h in all_hands if h.outcome == 'seven_out']
    avg_hand      = round(sum(hand_lengths) / len(hand_lengths), 1) if hand_lengths else 0
    longest_hand  = max(hand_lengths) if hand_lengths else 0

    return jsonify({
        "total_sessions": len(sessions),
        "total_rolls":    total_rolls,
        "total_hands":    len(all_hands),
        "lifetime_srr":   lifetime_srr,
        "lifetime_axis":  lifetime_axis,
        "avg_hand":       avg_hand,
        "longest_hand":   longest_hand,
    })
