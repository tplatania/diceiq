# ===============================
# Set Recommendation Engine
# The "zero the rifle scope" — drift-compensated set recommendations
#
# Takes a shooter's modal rotation signature and simulates what
# every possible dice set starting position produces AFTER their
# natural rotation is applied. Scores each set against the target
# and recommends the best one.
#
# "It does not tell the shooter to change how they throw.
#  It finds the set that meets them where they are."
#  — DiceIQ Section 15.7
#
# Usage:
#   from backend.services.recommendation_engine import recommend_best_set
#   result = recommend_best_set(
#       left_modal_x=2, left_modal_y=0, left_modal_z=0,
#       right_modal_x=3, right_modal_y=0, right_modal_z=0,
#       target="6_8"
#   )
# ===============================

from backend.services.dice_orientation import (
    ORIENTATIONS, TOP_FRONT_TO_IDX, IDX_TO_ORIENTATION,
    _rotate_x_forward, _rotate_x_backward,
    _rotate_y_left, _rotate_y_right,
    _rotate_z_right, _rotate_z_left,
)
from backend.services.dice_sets_seed import BUILT_IN_DICE_SETS


# -----------------------------------------------
# TARGET DEFINITIONS
# What numbers count as "hits" for each target
# -----------------------------------------------
TARGETS = {
    "srr":      {"avoid": {7}, "label": "Avoid Sevens (maximize SRR)"},
    "6_8":      {"hit": {6, 8}, "label": "Hit 6 and 8"},
    "5_9":      {"hit": {5, 9}, "label": "Hit 5 and 9"},
    "4_10":     {"hit": {4, 10}, "label": "Hit 4 and 10"},
    "all_box":  {"hit": {4, 5, 6, 8, 9, 10}, "label": "Hit all box numbers"},
    "come_out": {"hit": {7, 11}, "label": "Hit 7 or 11 on come-out"},
}


# -----------------------------------------------
# ROTATION APPLICATOR
# Apply a specific rotation (x, y, z) to an orientation index
# Returns the resulting orientation index, or None if invalid
# -----------------------------------------------

def apply_rotation(start_idx, x_rot, y_rot, z_rot):
    """
    Apply a sequence of rotations to a die starting at orientation index.
    x_rot: positive = forward pitches, negative = backward
    y_rot: positive = left yaw, negative = right yaw
    z_rot: positive = right roll, negative = left roll
    Returns final orientation index, or None if any step fails.
    """
    idx = start_idx

    # Apply X rotations (pitch)
    for _ in range(abs(x_rot)):
        if x_rot > 0:
            idx = _rotate_x_forward(idx)
        else:
            idx = _rotate_x_backward(idx)
        if idx is None:
            return None

    # Apply Y rotations (yaw)
    for _ in range(abs(y_rot)):
        if y_rot > 0:
            idx = _rotate_y_left(idx)
        else:
            idx = _rotate_y_right(idx)
        if idx is None:
            return None

    # Apply Z rotations (roll)
    for _ in range(abs(z_rot)):
        if z_rot > 0:
            idx = _rotate_z_right(idx)
        else:
            idx = _rotate_z_left(idx)
        if idx is None:
            return None

    return idx


# -----------------------------------------------
# SIMULATE SET OUTCOMES
# For a given set + shooter rotation, compute all 16 outcomes
# -----------------------------------------------

def simulate_set_with_rotation(dice_set, left_x, left_y, left_z,
                                right_x, right_y, right_z):
    """
    Given a dice set definition and a shooter's modal rotation per die,
    simulate all 16 on-axis outcomes (4 left pitches x 4 right pitches)
    with the shooter's Y/Z applied on top.

    The shooter's X value is NOT added to the pitch — the 4 pitch positions
    already represent all possible on-axis X outcomes (0,1,2,3 quarter turns).
    What matters is whether Y and Z deviation shift those outcomes.

    When left_x/right_x are non-zero, we PRE-COMPENSATE by shifting the
    starting position backward. This is the "zero the rifle scope" concept:
    if the shooter naturally pitches +1 extra, we start one pitch back
    so their natural throw lands on the intended position.

    Returns list of 16 totals (the top face sums after rotation).
    """
    lt = dice_set["left_top"]
    lf = dice_set["left_front"]
    rt = dice_set["right_top"]
    rf = dice_set["right_front"]

    # Pre-compensate starting position for X drift
    # If shooter pitches +1 extra, start 1 pitch backward
    left_start_idx = TOP_FRONT_TO_IDX.get((lt, lf))
    right_start_idx = TOP_FRONT_TO_IDX.get((rt, rf))

    if left_start_idx is None or right_start_idx is None:
        return []

    # Apply X pre-compensation (negative = undo the drift)
    if left_x != 0:
        comp = apply_rotation(left_start_idx, -left_x, 0, 0)
        if comp is not None:
            left_start_idx = comp

    if right_x != 0:
        comp = apply_rotation(right_start_idx, -right_x, 0, 0)
        if comp is not None:
            right_start_idx = comp

    totals = []

    # 4 possible X pitches per die (0, 1, 2, 3 quarter turns)
    # Y and Z from the shooter's natural throw are applied on top
    for left_pitch in range(4):
        for right_pitch in range(4):
            # Left die: standard pitch + shooter's Y/Z deviation
            left_final = apply_rotation(
                left_start_idx,
                left_pitch,
                left_y,
                left_z
            )
            # Right die: standard pitch + shooter's Y/Z deviation
            right_final = apply_rotation(
                right_start_idx,
                right_pitch,
                right_y,
                right_z
            )

            if left_final is not None and right_final is not None:
                left_top_val = ORIENTATIONS[left_final][0]
                right_top_val = ORIENTATIONS[right_final][0]
                totals.append(left_top_val + right_top_val)

    return totals


# -----------------------------------------------
# SCORE A SET AGAINST A TARGET
# -----------------------------------------------

def score_set(totals, target):
    """
    Score a set's 16 simulated outcomes against a target goal.

    For "srr": score = (16 - sevens) / 16   (fewer sevens = better)
    For hit targets: score = hits / 16       (more hits = better)

    Returns dict: { score, hits, sevens, total_outcomes }
    """
    if not totals:
        return {"score": 0, "hits": 0, "sevens": 0, "total_outcomes": 0}

    target_def = TARGETS.get(target, TARGETS["srr"])
    sevens = sum(1 for t in totals if t == 7)

    if "avoid" in target_def:
        # SRR mode — minimize sevens
        score = (len(totals) - sevens) / len(totals)
        hits = len(totals) - sevens
    else:
        # Hit mode — maximize target numbers
        hit_set = target_def["hit"]
        hits = sum(1 for t in totals if t in hit_set)
        score = hits / len(totals)

    return {
        "score": round(score, 4),
        "hits": hits,
        "sevens": sevens,
        "total_outcomes": len(totals),
    }


# -----------------------------------------------
# MAIN: RECOMMEND BEST SET
# The "zero the rifle scope" function
# -----------------------------------------------

def recommend_best_set(left_modal_x, left_modal_y, left_modal_z,
                       right_modal_x, right_modal_y, right_modal_z,
                       target="srr",
                       y_consistency=1.0, z_consistency=1.0):
    """
    Main entry point. Given a shooter's rotation signature,
    evaluate every built-in dice set and return the best one
    for the given target.

    Args:
        left_modal_x/y/z:  Most common rotation per axis, left die
        right_modal_x/y/z: Most common rotation per axis, right die
        target:            "srr", "6_8", "5_9", "4_10", "all_box", "come_out"
        y_consistency:     0-1, how consistent the Y axis is
        z_consistency:     0-1, how consistent the Z axis is

    Returns dict with:
        recommended_set, all_scores, coaching_note, compensation_note
    """

    # Safety: default None to 0
    lx = left_modal_x or 0
    ly = left_modal_y or 0
    lz = left_modal_z or 0
    rx = right_modal_x or 0
    ry = right_modal_y or 0
    rz = right_modal_z or 0

    # Check if axis control is too noisy for a meaningful recommendation
    if y_consistency < 0.40 or z_consistency < 0.40:
        noisy_axis = []
        if y_consistency < 0.40:
            noisy_axis.append("Y (yaw)")
        if z_consistency < 0.40:
            noisy_axis.append("Z (roll)")

        return {
            "status": "axis_too_noisy",
            "noisy_axes": noisy_axis,
            "coaching_note": (
                f"Your {' and '.join(noisy_axis)} rotation is too inconsistent "
                f"for a reliable set recommendation. A different dice set "
                f"can't fix a mechanical issue — focus on suppressing your "
                f"{' and '.join(noisy_axis)} deviation first. "
                f"Check the grip and release lessons in your training library."
            ),
            "recommended_set": None,
            "all_scores": [],
        }

    # Score every built-in set with the shooter's rotation applied
    results = []
    for dice_set in BUILT_IN_DICE_SETS:
        totals = simulate_set_with_rotation(
            dice_set, lx, ly, lz, rx, ry, rz
        )
        score_data = score_set(totals, target)

        # Also compute the "vanilla" score (no shooter rotation)
        vanilla_totals = simulate_set_with_rotation(
            dice_set, 0, 0, 0, 0, 0, 0
        )
        vanilla_score = score_set(vanilla_totals, target)

        results.append({
            "set_name": dice_set["name"],
            "description": dice_set["description"],
            "phase": dice_set.get("phase", "point"),
            "score": score_data["score"],
            "hits": score_data["hits"],
            "sevens": score_data["sevens"],
            "outcomes": score_data["total_outcomes"],
            "vanilla_score": vanilla_score["score"],
            "vanilla_hits": vanilla_score["hits"],
            "vanilla_sevens": vanilla_score["sevens"],
            "improvement": round(
                (score_data["score"] - vanilla_score["score"]) * 100, 1
            ),
        })

    # Sort by score descending — best set first
    results.sort(key=lambda r: r["score"], reverse=True)
    best = results[0]

    # Build the compensation note
    comp_parts = []
    if lx != 0:
        comp_parts.append(f"left die pitches {'+' if lx > 0 else ''}{lx}")
    if rx != 0:
        comp_parts.append(f"right die pitches {'+' if rx > 0 else ''}{rx}")
    if ly != 0:
        comp_parts.append(f"left die yaws {'+' if ly > 0 else ''}{ly}")
    if ry != 0:
        comp_parts.append(f"right die yaws {'+' if ry > 0 else ''}{ry}")

    compensation_note = ""
    if comp_parts:
        compensation_note = (
            f"Your natural rotation ({', '.join(comp_parts)}) "
            f"has been factored into this recommendation. "
            f"The {best['set_name']} set is positioned so your "
            f"natural throw lands on the target numbers."
        )

    # Build the reason
    target_label = TARGETS.get(target, TARGETS["srr"])["label"]
    if best["improvement"] > 0:
        reason = (
            f"For {target_label}, the {best['set_name']} set produces "
            f"{best['hits']} target hits out of {best['outcomes']} on-axis outcomes "
            f"with only {best['sevens']} sevens — when your natural rotation "
            f"is factored in. That is {best['improvement']}% better than "
            f"the textbook starting position."
        )
    else:
        reason = (
            f"For {target_label}, the {best['set_name']} set produces "
            f"{best['hits']} target hits out of {best['outcomes']} on-axis outcomes "
            f"with only {best['sevens']} sevens when your natural rotation "
            f"is applied."
        )

    return {
        "status": "ok",
        "target": target,
        "target_label": target_label,
        "recommended_set": best["set_name"],
        "reason": reason,
        "compensation_note": compensation_note,
        "best_score": best,
        "all_scores": results,
    }
