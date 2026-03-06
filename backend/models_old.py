"""
DiceIQ — Database Models
Every roll, every session, every diagnostic — stored forever.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# ─────────────────────────────────────────────────────────────
# SESSION
# One session = one visit to the table
# Could be 5 rolls or 500 rolls
# ─────────────────────────────────────────────────────────────

class Session(db.Model):
    __tablename__ = 'sessions'

    id            = db.Column(db.Integer, primary_key=True)
    started_at    = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at      = db.Column(db.DateTime, nullable=True)
    location      = db.Column(db.String(100), default="Ship Casino")
    dice_set      = db.Column(db.String(50),  default="Hardway")
    table_surface = db.Column(db.String(50),  nullable=True)
    notes         = db.Column(db.Text,        nullable=True)

    # Relationships
    rolls = db.relationship('Roll', backref='session',
                            lazy=True, cascade="all, delete-orphan")
    hands = db.relationship('Hand', backref='session',
                            lazy=True, cascade="all, delete-orphan")

    def summary(self):
        """Quick stats for this session"""
        total_rolls  = len(self.rolls)
        sevens       = sum(1 for r in self.rolls if r.total == 7)
        doubles      = sum(1 for r in self.rolls if r.left_die == r.right_die)
        srr          = round(total_rolls / sevens, 2) if sevens > 0 else 0
        axis_pct     = round((doubles / total_rolls) * 100, 1) if total_rolls > 0 else 0

        return {
            "session_id":   self.id,
            "started_at":   self.started_at.isoformat(),
            "location":     self.location,
            "dice_set":     self.dice_set,
            "total_rolls":  total_rolls,
            "total_hands":  len(self.hands),
            "sevens":       sevens,
            "srr":          srr,
            "axis_pct":     axis_pct,
        }

    def __repr__(self):
        return f"<Session {self.id} | {self.started_at.strftime('%Y-%m-%d %H:%M')}>"


# ─────────────────────────────────────────────────────────────
# HAND
# One hand = come-out roll through seven-out (or table end)
# Tracks how long Tom held the dice each time
# ─────────────────────────────────────────────────────────────

class Hand(db.Model):
    __tablename__ = 'hands'

    id          = db.Column(db.Integer, primary_key=True)
    session_id  = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    hand_number = db.Column(db.Integer, nullable=False)  # 1st hand, 2nd hand, etc.
    started_at  = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at    = db.Column(db.DateTime, nullable=True)
    point       = db.Column(db.Integer,  nullable=True)  # The established point (4-10)
    outcome     = db.Column(db.String(20), nullable=True) # 'seven_out', 'point_made', 'in_progress'

    # Relationships
    rolls = db.relationship('Roll', backref='hand',
                            lazy=True, cascade="all, delete-orphan")

    def roll_count(self):
        return len(self.rolls)

    def __repr__(self):
        return f"<Hand {self.hand_number} | Point:{self.point} | {self.outcome}>"


# ─────────────────────────────────────────────────────────────
# ROLL
# The atomic unit. Every single throw stored forever.
# ─────────────────────────────────────────────────────────────

class Roll(db.Model):
    __tablename__ = 'rolls'

    id          = db.Column(db.Integer, primary_key=True)
    session_id  = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    hand_id     = db.Column(db.Integer, db.ForeignKey('hands.id'),    nullable=False)
    roll_number = db.Column(db.Integer, nullable=False)  # Roll # within session
    timestamp   = db.Column(db.DateTime, default=datetime.utcnow)

    # The dice — left die always first (Tom's convention)
    left_die    = db.Column(db.Integer, nullable=False)  # 1-6
    right_die   = db.Column(db.Integer, nullable=False)  # 1-6
    total       = db.Column(db.Integer, nullable=False)  # 2-12

    # Game state at time of roll
    phase       = db.Column(db.String(20), nullable=False)  # 'come_out' or 'point'
    point       = db.Column(db.Integer,    nullable=True)   # Active point when rolled

    # Roll classification (calculated automatically)
    result_type = db.Column(db.String(20), nullable=False)
    # Possible values:
    #   'natural'     — come-out 7 or 11 (winner)
    #   'craps'       — come-out 2, 3, or 12 (loser)
    #   'point_set'   — come-out established a point
    #   'point_made'  — rolled the point (winner)
    #   'seven_out'   — rolled 7 during point phase (loser)
    #   'number'      — any other roll during point phase

    # Mechanical analysis
    is_double   = db.Column(db.Boolean, default=False)  # True if both dice match (on-axis indicator)
    on_axis     = db.Column(db.Boolean, nullable=True)  # Calculated from dice set vs result

    def to_dict(self):
        return {
            "id":          self.id,
            "roll_number": self.roll_number,
            "timestamp":   self.timestamp.isoformat(),
            "left_die":    self.left_die,
            "right_die":   self.right_die,
            "total":       self.total,
            "phase":       self.phase,
            "point":       self.point,
            "result_type": self.result_type,
            "is_double":   self.is_double,
            "on_axis":     self.on_axis,
        }

    def __repr__(self):
        return f"<Roll {self.roll_number} | {self.left_die}-{self.right_die} ({self.total}) | {self.result_type}>"


# ─────────────────────────────────────────────────────────────
# DIAGNOSTIC LOG
# The "Mechanical Audit" layer — fatigue alerts, axis warnings
# Written by Flask engine, read back by hearing aids
# ─────────────────────────────────────────────────────────────

class DiagnosticLog(db.Model):
    __tablename__ = 'diagnostic_logs'

    id          = db.Column(db.Integer, primary_key=True)
    session_id  = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    timestamp   = db.Column(db.DateTime, default=datetime.utcnow)
    roll_number = db.Column(db.Integer,  nullable=True)   # Which roll triggered this
    level       = db.Column(db.String(20), nullable=False) # 'info', 'warning', 'alert'
    category    = db.Column(db.String(50), nullable=False) # 'fatigue', 'axis', 'srr', 'signature'
    message     = db.Column(db.Text,       nullable=False) # What gets whispered in hearing aids

    # Examples of messages:
    # "SRR dropping — consider a break"
    # "Left die off-axis last 5 rolls — check finger pressure"
    # "Point made — great hand"
    # "40 rolls logged — fatigue window"

    def to_dict(self):
        return {
            "id":          self.id,
            "timestamp":   self.timestamp.isoformat(),
            "roll_number": self.roll_number,
            "level":       self.level,
            "category":    self.category,
            "message":     self.message,
        }

    def __repr__(self):
        return f"<Diagnostic [{self.level}] {self.category}: {self.message[:40]}>"
