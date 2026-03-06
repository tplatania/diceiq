# ===============================
# Session Model
# Running stats updated on every roll (no recalculation needed)
# Status tracking for multi-instance safety
# ===============================

from datetime import datetime, timezone
from backend.config import db


class Session(db.Model):
    __tablename__ = "sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    dice_set_id = db.Column(db.Integer, db.ForeignKey('dice_sets.id'), nullable=True)
    mode = db.Column(db.String(20), default="practice")
    status = db.Column(db.String(20), default="active")

    # Timestamps
    started_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    ended_at = db.Column(db.DateTime, nullable=True)
    last_roll_at = db.Column(db.DateTime, nullable=True)

    # Running stats (updated via SQL INCREMENT on every roll)
    total_rolls = db.Column(db.Integer, default=0)
    total_sevens = db.Column(db.Integer, default=0)
    total_doubles = db.Column(db.Integer, default=0)
    total_on_axis = db.Column(db.Integer, default=0)
    total_hands = db.Column(db.Integer, default=0)
    current_hand_rolls = db.Column(db.Integer, default=0)
    total_box_numbers = db.Column(db.Integer, default=0)  # 4,5,6,8,9,10 count for BSR

    # Per-number distribution — updated on every roll, powers bet strategy engine
    # JSON dict: {"2": 0, "3": 0, ..., "12": 0}
    number_distribution = db.Column(db.JSON, default=lambda: {
        str(n): 0 for n in range(2, 13)
    })

    # Computed at session end
    srr = db.Column(db.Float, nullable=True)
    axis_control_pct = db.Column(db.Float, nullable=True)
    avg_hand_length = db.Column(db.Float, nullable=True)
    longest_hand = db.Column(db.Integer, default=0)

    # Metadata
    notes = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(100), nullable=True)
    bankroll_start = db.Column(db.Float, nullable=True)
    bankroll_end = db.Column(db.Float, nullable=True)
    voice_session_token = db.Column(db.String(200), nullable=True)

    # Relationships
    rolls = db.relationship('Roll', backref='session', lazy=True, cascade='all, delete-orphan')
    hands = db.relationship('Hand', backref='session', lazy=True, cascade='all, delete-orphan')
    diagnostics = db.relationship('DiagnosticLog', backref='session', lazy=True, cascade='all, delete-orphan')

    def finalize(self):
        """
        Compute final stats when session ends.
        FIX: All division guarded — a session ended with 0 rolls is valid
        (shooter opened a session but never logged a throw).
        """
        self.status = "completed"
        self.ended_at = datetime.now(timezone.utc).replace(tzinfo=None)

        rolls   = self.total_rolls   or 0
        sevens  = self.total_sevens  or 0
        on_axis = self.total_on_axis or 0
        hands   = self.total_hands   or 0

        self.srr             = round(rolls / sevens,  2)  if sevens > 0 else None
        self.axis_control_pct = round((on_axis / rolls) * 100, 1) if rolls > 0 else None
        self.avg_hand_length  = round(rolls / hands, 1)   if hands  > 0 else None

    def summary(self):
        return {
            "id": self.id,
            "mode": self.mode,
            "status": self.status,
            "dice_set_id": self.dice_set_id,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "total_rolls": self.total_rolls,
            "total_hands": self.total_hands,
            "srr": self.srr if self.srr is not None else (round(self.total_rolls / self.total_sevens, 2) if self.total_sevens else None),
            "axis_control_pct": self.axis_control_pct if self.axis_control_pct is not None else (round(((self.total_on_axis or 0) / self.total_rolls) * 100, 1) if self.total_rolls else None),
            "longest_hand": self.longest_hand,
            "location": self.location,
        }
