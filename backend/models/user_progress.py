# ===============================
# UserProgress Model
# Tracks lesson completion per user
# ===============================

from datetime import datetime, timezone
from backend.config import db


class UserProgress(db.Model):
    __tablename__ = "user_progress"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    content_id = db.Column(db.Integer, db.ForeignKey('training_content.id'), nullable=False)
    progress_pct = db.Column(db.Float, default=0.0)
    started_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    completed_at = db.Column(db.DateTime, nullable=True)
