# ===============================
# DiagnosticLog Model
# Alerts and coaching messages during sessions
# ===============================

from datetime import datetime, timezone
from backend.config import db


class DiagnosticLog(db.Model):
    __tablename__ = "diagnostic_logs"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False, index=True)
    roll_number = db.Column(db.Integer, nullable=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    level = db.Column(db.String(20), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "roll_number": self.roll_number,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "level": self.level,
            "category": self.category,
            "message": self.message,
        }
