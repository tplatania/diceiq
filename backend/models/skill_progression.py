# ===============================
# SkillProgression Model
# Tracks milestones and achievements
# ===============================

from datetime import datetime, timezone
from backend.config import db


class SkillProgression(db.Model):
    __tablename__ = "skill_progressions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    milestone_type = db.Column(db.String(50), nullable=False)
    milestone_value = db.Column(db.String(100), nullable=True)
    points_awarded = db.Column(db.Integer, default=0)
    achieved_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
