# ===============================
# Hand Model
# One hand = come-out through seven-out
# ===============================

from datetime import datetime, timezone
from backend.config import db


class Hand(db.Model):
    __tablename__ = "hands"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False, index=True)
    hand_number = db.Column(db.Integer, nullable=False)
    started_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    ended_at = db.Column(db.DateTime, nullable=True)
    point = db.Column(db.Integer, nullable=True)
    outcome = db.Column(db.String(20), default="in_progress")
    roll_count = db.Column(db.Integer, default=0)

    rolls = db.relationship('Roll', backref='hand', lazy=True)
