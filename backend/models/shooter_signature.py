# ===============================
# ShooterSignature Model
# One row per user — their computed rotation signature
# Updated at the end of every session
# Powers the set recommendation engine
# ===============================

from datetime import datetime, timezone
from backend.config import db


class ShooterSignature(db.Model):
    __tablename__ = "shooter_signatures"

    id = db.Column(db.Integer, primary_key=True)

    # One active signature per user
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True, index=True)

    # Which set this signature was computed against
    dice_set_id = db.Column(db.Integer, db.ForeignKey('dice_sets.id'), nullable=True)

    # Sample size — confidence depends on this
    sessions_analyzed = db.Column(db.Integer, default=0)
    total_throws_analyzed = db.Column(db.Integer, default=0)

    # Left die — modal (most common) rotation per axis
    # Modal = the rotation value that appears most often across all throws
    left_modal_x = db.Column(db.Integer, nullable=True)
    left_modal_y = db.Column(db.Integer, nullable=True)
    left_modal_z = db.Column(db.Integer, nullable=True)

    # Left die — consistency scores (0.0 to 1.0)
    # How often the die matches its modal rotation on each axis
    left_x_consistency = db.Column(db.Float, nullable=True)
    left_y_consistency = db.Column(db.Float, nullable=True)
    left_z_consistency = db.Column(db.Float, nullable=True)

    # Right die — modal rotation per axis
    right_modal_x = db.Column(db.Integer, nullable=True)
    right_modal_y = db.Column(db.Integer, nullable=True)
    right_modal_z = db.Column(db.Integer, nullable=True)

    # Right die — consistency scores (0.0 to 1.0)
    right_x_consistency = db.Column(db.Float, nullable=True)
    right_y_consistency = db.Column(db.Float, nullable=True)
    right_z_consistency = db.Column(db.Float, nullable=True)

    # Overall axis control rating: poor / developing / controlled / elite
    axis_control_rating = db.Column(db.String(20), nullable=True)

    # Confidence score 0-100 based on sample size and consistency
    # <20 throws = no recommendation shown
    # 20-49 = low, 50-99 = medium, 100-199 = high, 200+ = very high
    signature_confidence = db.Column(db.Float, default=0.0)

    # Current set recommendation
    recommended_set_id = db.Column(db.Integer, db.ForeignKey('dice_sets.id'), nullable=True)
    recommendation_reason = db.Column(db.Text, nullable=True)

    # Optimization target: srr / 6_8 / 5_9 / 4_10 / point
    recommendation_target = db.Column(db.String(20), default="srr")

    # Housekeeping
    last_computed_at = db.Column(db.DateTime, nullable=True)
    needs_recompute = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "dice_set_id": self.dice_set_id,
            "sessions_analyzed": self.sessions_analyzed,
            "total_throws_analyzed": self.total_throws_analyzed,
            "left_modal_x": self.left_modal_x,
            "left_modal_y": self.left_modal_y,
            "left_modal_z": self.left_modal_z,
            "left_x_consistency": self.left_x_consistency,
            "left_y_consistency": self.left_y_consistency,
            "left_z_consistency": self.left_z_consistency,
            "right_modal_x": self.right_modal_x,
            "right_modal_y": self.right_modal_y,
            "right_modal_z": self.right_modal_z,
            "right_x_consistency": self.right_x_consistency,
            "right_y_consistency": self.right_y_consistency,
            "right_z_consistency": self.right_z_consistency,
            "axis_control_rating": self.axis_control_rating,
            "signature_confidence": self.signature_confidence,
            "recommended_set_id": self.recommended_set_id,
            "recommendation_reason": self.recommendation_reason,
            "recommendation_target": self.recommendation_target,
            "last_computed_at": self.last_computed_at.isoformat() if self.last_computed_at else None,
            "needs_recompute": self.needs_recompute,
        }
