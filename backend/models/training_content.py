# ===============================
# TrainingContent Model
# Lessons, videos, and interactive training
# ===============================

from backend.config import db


class TrainingContent(db.Model):
    __tablename__ = "training_content"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    skill_level = db.Column(db.String(20), default="all")
    content_type = db.Column(db.String(20), default="article")
    content_body = db.Column(db.Text, nullable=True)
    duration_minutes = db.Column(db.Integer, default=0)
    sort_order = db.Column(db.Integer, default=0)
    tier_required = db.Column(db.String(20), default="free")
    is_published = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "skill_level": self.skill_level,
            "content_type": self.content_type,
            "duration_minutes": self.duration_minutes,
            "tier_required": self.tier_required,
            "is_published": self.is_published,
        }
