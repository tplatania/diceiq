# ===============================
# Roll Model
# The atomic unit — every single throw stored forever
# ===============================

from datetime import datetime, timezone
from backend.config import db


class Roll(db.Model):
    __tablename__ = "rolls"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False, index=True)
    hand_id = db.Column(db.Integer, db.ForeignKey('hands.id'), nullable=True)
    roll_number = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    # The dice
    left_die = db.Column(db.Integer, nullable=False)
    right_die = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)

    # Game state
    phase = db.Column(db.String(20), nullable=True)
    point = db.Column(db.Integer, nullable=True)
    result_type = db.Column(db.String(20), nullable=True)

    # Mechanical analysis — basic
    is_double = db.Column(db.Boolean, default=False)
    on_axis = db.Column(db.Boolean, nullable=True)
    left_rotation = db.Column(db.String(20), nullable=True)   # legacy string, kept for compatibility
    right_rotation = db.Column(db.String(20), nullable=True)  # legacy string, kept for compatibility

    # Face capture — user speaks or enters after each throw
    # Convention: four numbers in order — left top, left front, right top, right front
    # "Front" = the face pointing toward the roller
    left_top_face = db.Column(db.Integer, nullable=True)    # Left die — face pointing up
    left_front_face = db.Column(db.Integer, nullable=True)  # Left die — face pointing toward roller
    right_top_face = db.Column(db.Integer, nullable=True)   # Right die — face pointing up
    right_front_face = db.Column(db.Integer, nullable=True) # Right die — face pointing toward roller

    # Rotation analysis — computed server-side from face capture + starting set
    # Positive = forward rotation, Negative = backward rotation
    left_x_rotation = db.Column(db.Integer, nullable=True)   # Left die pitch (forward/back)
    left_y_rotation = db.Column(db.Integer, nullable=True)   # Left die yaw (spin left/right)
    left_z_rotation = db.Column(db.Integer, nullable=True)   # Left die roll (sideways tilt)
    right_x_rotation = db.Column(db.Integer, nullable=True)  # Right die pitch (forward/back)
    right_y_rotation = db.Column(db.Integer, nullable=True)  # Right die yaw (spin left/right)
    right_z_rotation = db.Column(db.Integer, nullable=True)  # Right die roll (sideways tilt)

    # Rotation signature strings — e.g. "X+3,Y0,Z0" — computed server-side
    left_rotation_sig = db.Column(db.String(30), nullable=True)
    right_rotation_sig = db.Column(db.String(30), nullable=True)

    # Optional per-throw media and notes
    video_clip_url = db.Column(db.String(500), nullable=True)  # GCS URL for throw video
    throw_notes = db.Column(db.Text, nullable=True)            # User or coach notes

    # Index for post-session analytics
    __table_args__ = (
        db.Index('idx_rolls_session_total', 'session_id', 'total'),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "roll_number": self.roll_number,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "left_die": self.left_die,
            "right_die": self.right_die,
            "total": self.total,
            "phase": self.phase,
            "point": self.point,
            "result_type": self.result_type,
            "is_double": self.is_double,
            "on_axis": self.on_axis,
            # Face capture
            "left_top_face": self.left_top_face,
            "left_front_face": self.left_front_face,
            "right_top_face": self.right_top_face,
            "right_front_face": self.right_front_face,
            # Rotation analysis
            "left_x_rotation": self.left_x_rotation,
            "left_y_rotation": self.left_y_rotation,
            "left_z_rotation": self.left_z_rotation,
            "right_x_rotation": self.right_x_rotation,
            "right_y_rotation": self.right_y_rotation,
            "right_z_rotation": self.right_z_rotation,
            "left_rotation_sig": self.left_rotation_sig,
            "right_rotation_sig": self.right_rotation_sig,
            # Media
            "video_clip_url": self.video_clip_url,
            "throw_notes": self.throw_notes,
        }
