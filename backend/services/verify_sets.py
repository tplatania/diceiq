# ===============================
# Dice Set Verification Script
# Run this standalone to verify proposed dice set
# top/front orientations before seeding the database.
#
# Usage: python verify_sets.py
# ===============================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# -----------------------------------------------
# Inline orientation data (mirrors dice_orientation.py)
# Standalone so this runs without Flask context
# -----------------------------------------------

ORIENTATIONS = [
    (1, 2, 3, 6, 5, 4),  # 0
    (1, 3, 5, 6, 4, 2),  # 1
    (1, 5, 4, 6, 2, 3),  # 2
    (1, 4, 2, 6, 3, 5),  # 3
    (2, 1, 4, 5, 6, 3),  # 4
    (2, 4, 6, 5, 3, 1),  # 5
    (2, 6, 3, 5, 1, 4),  # 6
    (2, 3, 1, 5, 4, 6),  # 7
    (3, 1, 2, 4, 6, 5),  # 8
    (3, 2, 6, 4, 5, 1),  # 9
    (3, 6, 5, 4, 1, 2),  # 10
    (3, 5, 1, 4, 2, 6),  # 11
    (4, 1, 5, 3, 6, 2),  # 12
    (4, 5, 6, 3, 2, 1),  # 13
    (4, 6, 2, 3, 1, 5),  # 14
    (4, 2, 1, 3, 5, 6),  # 15
    (5, 1, 3, 2, 6, 4),  # 16
    (5, 3, 6, 2, 4, 1),  # 17
    (5, 6, 4, 2, 1, 3),  # 18
    (5, 4, 1, 2, 3, 6),  # 19
    (6, 2, 4, 1, 5, 3),  # 20
    (6, 4, 5, 1, 3, 2),  # 21
    (6, 5, 3, 1, 2, 4),  # 22
    (6, 3, 2, 1, 4, 5),  # 23
]

TOP_FRONT_TO_IDX = {(o[0], o[1]): i for i, o in enumerate(ORIENTATIONS)}

def get_full_orientation(top, front):
    """Return full (top, front, right, bottom, back, left) or None if invalid."""
    idx = TOP_FRONT_TO_IDX.get((top, front))
    if idx is None:
        return None
    return ORIENTATIONS[idx]


def get_all_axis_faces(top, front):
    """
    For a controlled on-axis throw (X-axis rotation only),
    the die rotates through 4 faces: top, front, bottom, back.
    Right and left faces never change — they stay on the axis.
    Returns the 4 axis faces as (top, front, bottom, back).
    """
    o = get_full_orientation(top, front)
    if o is None:
        return None
    top, front, right, bottom, back, left = o
    return (top, front, bottom, back)


def get_axis_totals(left_top, left_front, right_top, right_front):
    """
    For an on-axis throw, calculate all possible totals
    that can appear when both dice rotate on X axis only.
    Returns list of (left_face, right_face, total) tuples.
    """
    left_axis = get_all_axis_faces(left_top, left_front)
    right_axis = get_all_axis_faces(right_top, right_front)
    if left_axis is None or right_axis is None:
        return None

    results = []
    for l in left_axis:
        for r in right_axis:
            results.append((l, r, l + r))
    return results


def count_sevens_on_axis(left_top, left_front, right_top, right_front):
    """Count how many on-axis combinations produce a 7."""
    totals = get_axis_totals(left_top, left_front, right_top, right_front)
    if totals is None:
        return -1
    return sum(1 for l, r, t in totals if t == 7)


def verify_set(name, left_top, left_front, right_top, right_front):
    """
    Full verification of a proposed dice set orientation.
    Prints a detailed report.
    """
    print(f"\n{'='*55}")
    print(f"  SET: {name}")
    print(f"  Left die:  top={left_top}, front={left_front}")
    print(f"  Right die: top={right_top}, front={right_front}")
    print(f"{'='*55}")

    # Validate both orientations
    left_o = get_full_orientation(left_top, left_front)
    right_o = get_full_orientation(right_top, right_front)

    if left_o is None:
        print(f"  ERROR: Invalid left die orientation ({left_top},{left_front})")
        return
    if right_o is None:
        print(f"  ERROR: Invalid right die orientation ({right_top},{right_front})")
        return

    print(f"\n  Left die full state:")
    print(f"    top={left_o[0]} front={left_o[1]} right={left_o[2]}")
    print(f"    bottom={left_o[3]} back={left_o[4]} left={left_o[5]}")

    print(f"\n  Right die full state:")
    print(f"    top={right_o[0]} front={right_o[1]} right={right_o[2]}")
    print(f"    bottom={right_o[3]} back={right_o[4]} left={right_o[5]}")

    # On-axis outcomes
    totals = get_axis_totals(left_top, left_front, right_top, right_front)
    sevens = count_sevens_on_axis(left_top, left_front, right_top, right_front)

    print(f"\n  On-axis outcomes (all 16 combinations):")
    for l, r, t in totals:
        marker = " <-- SEVEN" if t == 7 else ""
        print(f"    {l} + {r} = {t}{marker}")

    print(f"\n  Seven count on axis: {sevens} / 16")
    print(f"  Starting total (top faces): {left_top + right_top}")
    print(f"  Starting front total: {left_front + right_front}")


# -----------------------------------------------
# PROPOSED SET ORIENTATIONS
# These are the candidates to verify
# -----------------------------------------------

PROPOSED_SETS = [
    # name,            L-top  L-front  R-top  R-front
    ("Hard Way",          2,     3,      2,     4),
    ("All Sevens",        3,     4,      4,     3),
    ("3V Set",            3,     2,      3,     5),
    ("2V Set",            2,     1,      2,     6),
    ("Crossed Sixes",     6,     2,      6,     5),
    ("5V Set",            5,     1,      5,     6),
    ("Straight Sixes",    6,     2,      6,     2),
]


if __name__ == "__main__":
    print("\nDICEIQ — DICE SET VERIFICATION REPORT")
    print("Verifying top/front orientations and on-axis outcomes\n")

    for name, lt, lf, rt, rf in PROPOSED_SETS:
        verify_set(name, lt, lf, rt, rf)

    print(f"\n{'='*55}")
    print("  Verification complete.")
    print(f"{'='*55}\n")
