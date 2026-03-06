# ===============================
# User Model
# Authentication, subscription, skill tracking
# ===============================

from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from backend.config import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    display_name = db.Column(db.String(100), nullable=True)
    profile_picture_url = db.Column(db.String(500), nullable=True)

    # Password reset
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)

    # Subscription
    subscription_tier = db.Column(db.String(20), default="free")
    stripe_customer_id = db.Column(db.String(100), nullable=True)
    stripe_subscription_id = db.Column(db.String(100), nullable=True)

    # Skill progression
    skill_level = db.Column(db.String(20), default="beginner")
    skill_points = db.Column(db.Integer, default=0)

    # Usage tracking
    voice_minutes_used = db.Column(db.Float, default=0.0)
    monthly_session_count = db.Column(db.Integer, default=0)
    last_reset_date = db.Column(db.DateTime, nullable=True)

    # Preferences
    preferred_dice_set = db.Column(db.String(50), default="Hard Way")

    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    last_login = db.Column(db.DateTime, nullable=True)

    # Relationships
    sessions = db.relationship('Session', backref='owner', lazy=True, cascade='all, delete-orphan')
    dice_sets = db.relationship('DiceSet', backref='creator', lazy=True, cascade='all, delete-orphan')
    stats = db.relationship('UserStats', backref='owner', uselist=False, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_voice_minutes_limit(self):
        limits = {"free": 5.0, "pro": 60.0, "elite": 180.0, "academy": 180.0}
        return limits.get(self.subscription_tier, 5.0)

    def get_voice_minutes_remaining(self):
        return max(0, self.get_voice_minutes_limit() - (self.voice_minutes_used or 0.0))

    def can_use_voice(self, minutes_needed=0.1):
        if self.subscription_tier == "free" and (self.voice_minutes_used or 0.0) >= 5.0:
            return False
        return self.get_voice_minutes_remaining() >= minutes_needed

    def get_session_limit(self):
        """Max rolls per session by tier"""
        limits = {"free": 30, "pro": 999999, "elite": 999999, "academy": 999999}
        return limits.get(self.subscription_tier, 30)

    def reset_monthly_counts(self):
        self.monthly_session_count = 0
        self.voice_minutes_used = 0.0
        self.last_reset_date = datetime.now(timezone.utc).replace(tzinfo=None)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "display_name": self.display_name,
            "profile_picture_url": self.profile_picture_url,
            "subscription_tier": self.subscription_tier,
            "skill_level": self.skill_level,
            "skill_points": self.skill_points,
            "voice_minutes_used": self.voice_minutes_used or 0.0,
            "voice_minutes_remaining": self.get_voice_minutes_remaining(),
            "voice_minutes_limit": self.get_voice_minutes_limit(),
            "session_roll_limit": self.get_session_limit(),
            "preferred_dice_set": self.preferred_dice_set,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }
