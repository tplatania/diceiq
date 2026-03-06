# ===============================
# Dice Sets Seed Data
# Built-in sets verified against orientation engine
# Source: Axis Power Craps (axispowercraps.com)
# All on-axis distributions mathematically verified
#
# Orientation convention:
#   top   = face pointing up
#   front = face pointing toward the roller
#
# on_axis_outcomes = hit counts per number out of 16
# target_numbers   = what this set is designed to produce
# seven_count      = how many of 16 on-axis combos produce 7
# ===============================

BUILT_IN_DICE_SETS = [
    {
        "name": "All Sevens",
        "set_type": "builtin",
        "description": (
            "Maximum sevens on every axis face. "
            "The go-to set for the come out roll — "
            "every on-axis face combination produces a 7 or natural. "
            "Switch to another set once a point is established."
        ),
        "left_top": 4,
        "left_front": 2,
        "right_top": 3,
        "right_front": 5,
        "target_numbers": [7],
        "target_label": "Hit 7 on come out",
        "seven_count": 4,
        "target_hits": 4,
        "target_pct": 25,
        "seven_pct": 25,
        "on_axis_outcomes": {
            "4": 1, "5": 2, "6": 3, "7": 4,
            "8": 3, "9": 2, "10": 1
        },
        "skill_level_required": "beginner",
        "phase": "come_out",
    },
    {
        "name": "Hard Way",
        "set_type": "builtin",
        "description": (
            "The most popular beginner set. "
            "Hardway numbers on top provide a visual reference. "
            "Best for surviving the point phase — "
            "no specific number targeted, just seven avoidance. "
            "Note: does not hit 5 or 9 on axis."
        ),
        "left_top": 6,
        "left_front": 5,
        "right_top": 6,
        "right_front": 5,
        "target_numbers": [7],
        "target_label": "Avoid 7, survive point phase",
        "seven_count": 4,
        "target_hits": 4,
        "target_pct": 25,
        "seven_pct": 25,
        "on_axis_outcomes": {
            "2": 1, "3": 2, "4": 1, "6": 2, "7": 4,
            "8": 2, "10": 1, "11": 2, "12": 1
        },
        "skill_level_required": "beginner",
        "phase": "point",
    },
    {
        "name": "3V Hard Six",
        "set_type": "builtin",
        "description": (
            "3s form a V on top. Best seven protection of any "
            "six-and-eight set — only 2 sevens on axis out of 16. "
            "Loads up on 6 and 8 with 3 ways each. "
            "The preferred set for inside number players "
            "who want maximum protection."
        ),
        "left_top": 3,
        "left_front": 2,
        "right_top": 3,
        "right_front": 6,
        "target_numbers": [6, 8],
        "target_label": "Hit 6 and 8",
        "seven_count": 2,
        "target_hits": 6,
        "target_pct": 38,
        "seven_pct": 12,
        "on_axis_outcomes": {
            "3": 1, "4": 1, "5": 2, "6": 3, "7": 2,
            "8": 3, "9": 2, "10": 1, "11": 1
        },
        "skill_level_required": "intermediate",
        "phase": "point",
    },
    {
        "name": "Parallel Sixes",
        "set_type": "builtin",
        "description": (
            "Both 6s on top running parallel. "
            "Targets outside numbers — 4, 5, 9, and 10. "
            "Hits all four outside numbers equally at 2 ways each. "
            "Total of 8 outside hits vs 4 sevens on axis. "
            "Great for shooters who prefer place bets on 4 and 10."
        ),
        "left_top": 6,
        "left_front": 3,
        "right_top": 6,
        "right_front": 3,
        "target_numbers": [4, 5, 9, 10],
        "target_label": "Hit outside numbers 4, 5, 9, 10",
        "seven_count": 4,
        "target_hits": 8,
        "target_pct": 50,
        "seven_pct": 25,
        "on_axis_outcomes": {
            "2": 1, "4": 2, "5": 2, "6": 1, "7": 4,
            "8": 1, "9": 2, "10": 2, "12": 1
        },
        "skill_level_required": "intermediate",
        "phase": "point",
    },
    {
        "name": "Crossed Sixes",
        "set_type": "builtin",
        "description": (
            "6s crossed when viewed from above. "
            "The best all-around set for box number players. "
            "Covers all six box numbers with 10 target hits out of 16 "
            "and only 2 sevens on axis — the highest target percentage "
            "with the best seven protection of any set. "
            "Ideal for shooters with place bets across the board."
        ),
        "left_top": 6,
        "left_front": 2,
        "right_top": 6,
        "right_front": 3,
        "target_numbers": [4, 5, 6, 8, 9, 10],
        "target_label": "Hit all box numbers",
        "seven_count": 2,
        "target_hits": 10,
        "target_pct": 62,
        "seven_pct": 12,
        "on_axis_outcomes": {
            "2": 1, "3": 1, "4": 1, "5": 2, "6": 2, "7": 2,
            "8": 2, "9": 2, "10": 1, "11": 1, "12": 1
        },
        "skill_level_required": "advanced",
        "phase": "point",
    },
    {
        "name": "Mini-V Hard 4",
        "set_type": "builtin",
        "description": (
            "A V formation using 3 and 2. "
            "Targets 5 and 9 specifically. "
            "Hits 5 and 9 with 2 ways each for 4 total target hits. "
            "Also produces strong 6 and 8 coverage as a bonus. "
            "Good for shooters focused on 5 and 9 place bets."
        ),
        "left_top": 3,
        "left_front": 2,
        "right_top": 2,
        "right_front": 3,
        "target_numbers": [5, 9],
        "target_label": "Hit 5 and 9",
        "seven_count": 4,
        "target_hits": 4,
        "target_pct": 25,
        "seven_pct": 25,
        "on_axis_outcomes": {
            "4": 1, "5": 2, "6": 3, "7": 4,
            "8": 3, "9": 2, "10": 1
        },
        "skill_level_required": "intermediate",
        "phase": "point",
    },
    {
        "name": "2V Set",
        "set_type": "builtin",
        "description": (
            "2s form a V on top. Excellent seven protection — "
            "only 2 sevens on axis out of 16. "
            "Targets 4 and 10 with 2 ways each. "
            "Also the most balanced set for all point numbers — "
            "every number from 4 through 10 hits equally at 2 ways. "
            "Great for outside number players who want protection."
        ),
        "left_top": 2,
        "left_front": 3,
        "right_top": 2,
        "right_front": 1,
        "target_numbers": [4, 10],
        "target_label": "Hit 4 and 10",
        "seven_count": 2,
        "target_hits": 4,
        "target_pct": 25,
        "seven_pct": 12,
        "on_axis_outcomes": {
            "3": 1, "4": 2, "5": 2, "6": 2, "7": 2,
            "8": 2, "9": 2, "10": 2, "11": 1
        },
        "skill_level_required": "intermediate",
        "phase": "point",
    },
]


# ===============================
# Seed Function
# Call once on first run to populate built-in dice sets
# Safe to run multiple times — skips existing sets by name
# ===============================

def seed_dice_sets(db, DiceSet):
    """
    Insert built-in dice sets into the database.
    Skips any set that already exists by name.
    Returns count of sets inserted.
    """
    inserted = 0
    for s in BUILT_IN_DICE_SETS:
        existing = DiceSet.query.filter_by(name=s["name"], set_type="builtin").first()
        if existing:
            continue
        dice_set = DiceSet(
            user_id=None,
            name=s["name"],
            set_type=s["set_type"],
            description=s["description"],
            top_faces={
                "left": s["left_top"],
                "right": s["right_top"],
            },
            front_faces={
                "left": s["left_front"],
                "right": s["right_front"],
            },
            on_axis_outcomes=s["on_axis_outcomes"],
            seven_positions={
                "seven_count": s["seven_count"],
                "target_hits": s["target_hits"],
                "target_pct": s["target_pct"],
                "seven_pct": s["seven_pct"],
                "target_numbers": s["target_numbers"],
                "target_label": s["target_label"],
            },
            skill_level_required=s["skill_level_required"],
            is_active=True,
        )
        db.session.add(dice_set)
        inserted += 1

    if inserted > 0:
        db.session.commit()
        print(f"--- Seeded {inserted} built-in dice sets ---")
    else:
        print("--- Built-in dice sets already seeded ---")

    return inserted
