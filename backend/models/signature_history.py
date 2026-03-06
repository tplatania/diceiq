# ===============================
# SignatureHistory Model
# Snapshot of a shooter's signature — written at session end OR manual era reset.
# Enables trend analysis — are they getting more consistent over time?
# Never updated — append-only, permanent record.
#
# session_id is nullable because a manual era reset ("Start New Baseline")
# archives the current era without being tied to a specific session.
# ===============================

from datetime import datetime, timezone
from backend.config import db


class SignatureHistory(db.Model):
    __tablename__ = "signature_history"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    # nullable=True — manual era resets are not tied to any specific session
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=True, index=True)

    # How this snapshot was created: 'session_end' or 'manual_reset'
    snapshot_type = db.Column(db.String(20), default='session_end')

    # Snapshot values at the time this session ended
    # Mirrors ShooterSignature fields — point in time record
    sessions_analyzed = db.Column(db.Integer, nullable=True)
    total_throws_analyzed = db.Column(db.Integer, nullable=True)

    # Left die snapshot
    left_modal_x = db.Column(db.Integer, nullable=True)
    left_modal_y = db.Column(db.Integer, nullable=True)
    left_modal_z = db.Column(db.Integer, nullable=True)
    left_x_consistency = db.Column(db.Float, nullable=True)
    left_y_consistency = db.Column(db.Float, nullable=True)
    left_z_consistency = db.Column(db.Float, nullable=True)

    # Right die snapshot
    right_modal_x = db.Column(db.Integer, nullable=True)
    right_modal_y = db.Column(db.Integer, nullable=True)
    right_modal_z = db.Column(db.Integer, nullable=True)
    right_x_consistency = db.Column(db.Float, nullable=True)
    right_y_consistency = db.Column(db.Float, nullable=True)
    right_z_consistency = db.Column(db.Float, nullable=True)

    # Assessment snapshot
    axis_control_rating = db.Column(db.String(20), nullable=True)
    signature_confidence = db.Column(db.Float, nullable=True)

    # What set was recommended at this point in time
    recommended_set_id = db.Column(db.Integer, db.ForeignKey('dice_sets.id'), nullable=True)
    recommendation_target = db.Column(db.String(20), nullable=True)

    # When this snapshot was taken
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "snapshot_type": self.snapshot_type,
            "sessions_analyzed": self.sessions_analyzed,
            "total_throws_analyzed": self.total_throws_analyzed,
            # Left die
            "left_modal_x": self.left_modal_x,
            "left_modal_y": self.left_modal_y,
            "left_modal_z": self.left_modal_z,
            "left_x_consistency": self.left_x_consistency,
            "left_y_consistency": self.left_y_consistency,
            "left_z_consistency": self.left_z_consistency,
            # Right die
            "right_modal_x": self.right_modal_x,
            "right_modal_y": self.right_modal_y,
            "right_modal_z": self.right_modal_z,
            "right_x_consistency": self.right_x_consistency,
            "right_y_consistency": self.right_y_consistency,
            "right_z_consistency": self.right_z_consistency,
            # Assessment
            "axis_control_rating": self.axis_control_rating,
            "signature_confidence": self.signature_confidence,
            "recommended_set_id": self.recommended_set_id,
            "recommendation_target": self.recommendation_target,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
