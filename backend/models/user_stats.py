# ===============================
# UserStats Model
# Pre-computed lifetime statistics
# Updated at session end, avoids scanning millions of rolls
# ===============================

from datetime import datetime, timezone
from backend.config import db


class UserStats(db.Model):
    __tablename__ = "user_stats"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False, index=True)

    # Lifetime counters (incremented at session end)
    lifetime_rolls = db.Column(db.Integer, default=0)
    lifetime_sevens = db.Column(db.Integer, default=0)
    lifetime_doubles = db.Column(db.Integer, default=0)
    lifetime_on_axis = db.Column(db.Integer, default=0)
    lifetime_box_numbers = db.Column(db.Integer, default=0)
    lifetime_sessions = db.Column(db.Integer, default=0)

    # Lifetime number distribution — powers bet strategy knowledge base
    # JSON dict: {"2": 0, "3": 0, ..., "12": 0}
    lifetime_number_distribution = db.Column(db.JSON, default=lambda: {
        str(n): 0 for n in range(2, 13)
    })

    # Pre-computed metrics
    lifetime_srr = db.Column(db.Float, default=0.0)
    lifetime_axis_pct = db.Column(db.Float, default=0.0)
    lifetime_avg_hand = db.Column(db.Float, default=0.0)
    longest_hand_ever = db.Column(db.Integer, default=0)
    best_session_srr = db.Column(db.Float, default=0.0)

    # Recompute tracking
    last_computed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    needs_recompute = db.Column(db.Boolean, default=False)

    def update_from_session(self, session):
        """Incrementally update lifetime stats from a completed session"""
        self.lifetime_rolls += session.total_rolls or 0
        self.lifetime_sevens += session.total_sevens or 0
        self.lifetime_doubles += session.total_doubles or 0
        self.lifetime_on_axis += session.total_on_axis or 0
        self.lifetime_box_numbers += session.total_box_numbers or 0
        self.lifetime_sessions += 1

        # Merge session number distribution into lifetime
        session_dist = session.number_distribution or {}
        lifetime_dist = self.lifetime_number_distribution or {str(n): 0 for n in range(2, 13)}
        for num, count in session_dist.items():
            lifetime_dist[num] = lifetime_dist.get(num, 0) + count
        self.lifetime_number_distribution = lifetime_dist

        # Recompute derived metrics
        if self.lifetime_sevens > 0:
            self.lifetime_srr = round(self.lifetime_rolls / self.lifetime_sevens, 2)
        if self.lifetime_rolls > 0:
            self.lifetime_axis_pct = round((self.lifetime_on_axis / self.lifetime_rolls) * 100, 1)

        # Track bests
        session_srr = session.srr or 0
        if session_srr > (self.best_session_srr or 0):
            self.best_session_srr = session_srr
        session_longest = session.longest_hand or 0
        if session_longest > (self.longest_hand_ever or 0):
            self.longest_hand_ever = session_longest

        # Update lifetime average hand length
        # Uses lifetime SRR as proxy: avg hand = SRR (rolls between sevens)
        if self.lifetime_sevens > 0:
            self.lifetime_avg_hand = round(self.lifetime_rolls / self.lifetime_sevens, 1)

        self.last_computed_at = datetime.now(timezone.utc).replace(tzinfo=None)

    def to_dict(self):
        lifetime_bsr = None
        if self.lifetime_sevens and self.lifetime_sevens > 0:
            lifetime_bsr = round(self.lifetime_box_numbers / self.lifetime_sevens, 2)
        return {
            "lifetime_rolls": self.lifetime_rolls,
            "lifetime_sevens": self.lifetime_sevens,
            "lifetime_box_numbers": self.lifetime_box_numbers,
            "lifetime_srr": self.lifetime_srr,
            "lifetime_bsr": lifetime_bsr,
            "lifetime_axis_pct": self.lifetime_axis_pct,
            "lifetime_avg_hand": self.lifetime_avg_hand,
            "lifetime_sessions": self.lifetime_sessions,
            "longest_hand_ever": self.longest_hand_ever,
            "best_session_srr": self.best_session_srr,
            "lifetime_number_distribution": self.lifetime_number_distribution,
        }
