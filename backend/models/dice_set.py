# ===============================
# DiceSet Model
# Built-in and user-created custom dice sets
# ===============================

from datetime import datetime, timezone
from backend.config import db


class DiceSet(db.Model):
    __tablename__ = "dice_sets"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    name = db.Column(db.String(100), nullable=False)
    set_type = db.Column(db.String(20), nullable=False)
    top_faces = db.Column(db.JSON, nullable=True)
    front_faces = db.Column(db.JSON, nullable=True)
    on_axis_outcomes = db.Column(db.JSON, nullable=True)
    seven_positions = db.Column(db.JSON, nullable=True)
    description = db.Column(db.Text, nullable=True)
    skill_level_required = db.Column(db.String(20), default="beginner")
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "set_type": self.set_type,
            "on_axis_outcomes": self.on_axis_outcomes,
            "description": self.description,
            "skill_level_required": self.skill_level_required,
            "is_active": self.is_active,
            "is_custom": self.user_id is not None,
        }
