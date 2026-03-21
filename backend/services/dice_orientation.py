# ===============================
# Dice Orientation Engine
# The mathematical core of DiceIQ
#
# A standard Western die has 24 possible orientations.
# Any two adjacent faces (top + front) uniquely define
# the complete 3D orientation of the die.
#
# Convention:
#   top   = face pointing up (toward ceiling)
#   front = face pointing toward the roller
#
# Opposite faces always sum to 7:
#   1 opposite 6, 2 opposite 5, 3 opposite 4
# ===============================


# -----------------------------------------------
# ORIENTATION MAP
# Every valid (top, front) pair mapped to a
# canonical orientation index (0-23).
# Used to look up the full die state instantly.
# -----------------------------------------------

# Each orientation is defined as:
# (top, front, right, bottom, back, left)
# bottom = 7 - top, back = 7 - front, left = 7 - right

ORIENTATIONS = [
    # idx: (top, front, right, bottom, back, left)
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

# -----------------------------------------------
# LOOKUP TABLES
# Built once at import time for O(1) lookups
# -----------------------------------------------

# (top, front) -> orientation index
TOP_FRONT_TO_IDX = {
    (o[0], o[1]): i for i, o in enumerate(ORIENTATIONS)
}

# orientation index -> full tuple (top, front, right, bottom, back, left)
IDX_TO_ORIENTATION = {i: o for i, o in enumerate(ORIENTATIONS)}


def get_orientation(top, front):
    """
    Given top and front face values, return the full orientation tuple.
    Returns None if the combination is invalid.
    """
    idx = TOP_FRONT_TO_IDX.get((top, front))
    if idx is None:
        return None
    return IDX_TO_ORIENTATION[idx]


def get_orientation_index(top, front):
    """
    Return the orientation index (0-23) for a given top + front pair.
    Returns None if invalid.
    """
    return TOP_FRONT_TO_IDX.get((top, front))


def is_valid_orientation(top, front):
    """
    Check whether a top + front face combination is valid.
    Invalid example: top=1, front=6 (opposite faces — impossible).
    """
    return (top, front) in TOP_FRONT_TO_IDX


# -----------------------------------------------
# ROTATION OPERATIONS
# Apply a single 90-degree rotation to an orientation
# Returns the new orientation index after rotation
# -----------------------------------------------

def _rotate_x_forward(idx):
    """
    Pitch forward 90 degrees — die tumbles toward the back wall.
    Top face becomes back, front face becomes top.
    """
    top, front, right, bottom, back, left = ORIENTATIONS[idx]
    # After pitching forward: new top=front, new front=bottom, new bottom=back, new back=top
    return TOP_FRONT_TO_IDX.get((front, bottom))


def _rotate_x_backward(idx):
    """
    Pitch backward 90 degrees — die tumbles toward the roller.
    """
    top, front, right, bottom, back, left = ORIENTATIONS[idx]
    # After pitching backward: new top=back, new front=top
    return TOP_FRONT_TO_IDX.get((back, top))


def _rotate_y_left(idx):
    """
    Yaw left 90 degrees — die spins counterclockwise when viewed from above.
    """
    top, front, right, bottom, back, left = ORIENTATIONS[idx]
    # After yaw left: new front=right, new right=back
    return TOP_FRONT_TO_IDX.get((top, right))


def _rotate_y_right(idx):
    """
    Yaw right 90 degrees — die spins clockwise when viewed from above.
    """
    top, front, right, bottom, back, left = ORIENTATIONS[idx]
    # After yaw right: new front=left
    return TOP_FRONT_TO_IDX.get((top, left))


def _rotate_z_right(idx):
    """
    Roll right 90 degrees — die tilts to the right.
    """
    top, front, right, bottom, back, left = ORIENTATIONS[idx]
    # After rolling right: new top=left, new right=top
    return TOP_FRONT_TO_IDX.get((left, front))


def _rotate_z_left(idx):
    """
    Roll left 90 degrees — die tilts to the left.
    """
    top, front, right, bottom, back, left = ORIENTATIONS[idx]
    # After rolling left: new top=right
    return TOP_FRONT_TO_IDX.get((right, front))


# -----------------------------------------------
# ROTATION CALCULATION
# Given a starting orientation and an ending
# orientation, calculate the X/Y/Z rotations.
# -----------------------------------------------

def calculate_rotations(start_top, start_front, end_top, end_front):
    """
    Calculate the X, Y, Z rotations between two die orientations.

    Args:
        start_top:   Top face at start (from dice set definition)
        start_front: Front face at start (from dice set definition)
        end_top:     Top face after throw (user reported)
        end_front:   Front face after throw (user reported)

    Returns:
        dict with keys: x, y, z, signature, valid
        x = pitch rotations (positive = forward, negative = backward)
        y = yaw rotations (positive = left, negative = right)
        z = roll rotations (positive = right, negative = left)
        signature = string e.g. "X+3,Y0,Z0"
        valid = False if any face combination is invalid
    """
    if not is_valid_orientation(start_top, start_front):
        return {"valid": False, "error": f"Invalid start orientation: top={start_top}, front={start_front}"}
    if not is_valid_orientation(end_top, end_front):
        return {"valid": False, "error": f"Invalid end orientation: top={end_top}, front={end_front}"}

    start_idx = get_orientation_index(start_top, start_front)
    end_idx = get_orientation_index(end_top, end_front)

    if start_idx == end_idx:
        return {"valid": True, "x": 0, "y": 0, "z": 0, "signature": "X0,Y0,Z0"}

    # BFS — find shortest rotation path from start to end
    # Each step is one 90-degree rotation on any axis
    from collections import deque

    MOVES = [
        ("x", +1, _rotate_x_forward),
        ("x", -1, _rotate_x_backward),
        ("y", +1, _rotate_y_left),
        ("y", -1, _rotate_y_right),
        ("z", +1, _rotate_z_right),
        ("z", -1, _rotate_z_left),
    ]

    # State: (current_idx, x_count, y_count, z_count)
    queue = deque([(start_idx, 0, 0, 0)])
    visited = {start_idx}

    while queue:
        curr_idx, x, y, z = queue.popleft()
        for axis, direction, rotate_fn in MOVES:
            next_idx = rotate_fn(curr_idx)
            if next_idx is None:
                continue
            nx = x + direction if axis == "x" else x
            ny = y + direction if axis == "y" else y
            nz = z + direction if axis == "z" else z
            if next_idx == end_idx:
                sig = f"X{'+' if nx >= 0 else ''}{nx},Y{'+' if ny >= 0 else ''}{ny},Z{'+' if nz >= 0 else ''}{nz}"
                return {"valid": True, "x": nx, "y": ny, "z": nz, "signature": sig}
            if next_idx not in visited:
                visited.add(next_idx)
                queue.append((next_idx, nx, ny, nz))

    return {"valid": False, "error": "Could not find rotation path"}


def build_rotation_signature(x, y, z):
    """
    Build the signature string from integer rotation values.
    e.g. x=3, y=0, z=-1 -> "X+3,Y0,Z-1"
    """
    def fmt(val):
        return f"+{val}" if val > 0 else str(val)
    return f"X{fmt(x)},Y{fmt(y)},Z{fmt(z)}"


# -----------------------------------------------
# PRESET DICE SETS
# Each set defined by (left_top, left_front, right_top, right_front)
# These are the 7 built-in DiceIQ sets.
# -----------------------------------------------

PRESET_SETS = [
    {"name": "All Sevens",     "lt": 4, "lf": 2, "rt": 3, "rf": 5,
     "targets": [7],           "phase": "come_out"},
    {"name": "Hard Way",       "lt": 6, "lf": 5, "rt": 6, "rf": 5,
     "targets": [4,5,6,8,9,10], "phase": "point"},
    {"name": "3V Hard Six",    "lt": 3, "lf": 2, "rt": 3, "rf": 6,
     "targets": [6, 8],        "phase": "point"},
    {"name": "Straight Sixes", "lt": 6, "lf": 5, "rt": 6, "rf": 5,
     "targets": [7],           "phase": "come_out"},
    {"name": "Crossed Sixes",  "lt": 6, "lf": 2, "rt": 6, "rf": 3,
     "targets": [4,5,6,8,9,10], "phase": "point"},
    {"name": "Mini-V Hard 4",  "lt": 3, "lf": 2, "rt": 2, "rf": 3,
     "targets": [5, 9],        "phase": "point"},
    {"name": "2V Set",         "lt": 2, "lf": 3, "rt": 2, "rf": 1,
     "targets": [4, 10],       "phase": "point"},
]


# -----------------------------------------------
# APPLY ROTATION SIGNATURE TO A DIE
# Given a starting orientation index and X/Y/Z
# rotation counts, apply the rotations and return
# the resulting orientation index.
# -----------------------------------------------

def apply_rotations(start_idx, x_rot, y_rot, z_rot):
    """
    Apply a sequence of rotations to a die.
    x_rot: pitch rotations (positive=forward, negative=backward)
    y_rot: yaw rotations (positive=left, negative=right)
    z_rot: roll rotations (positive=right, negative=left)
    Returns the final orientation index, or None if invalid.
    """
    idx = start_idx

    # Apply X rotations (pitch)
    x_fn = _rotate_x_forward if x_rot >= 0 else _rotate_x_backward
    for _ in range(abs(x_rot)):
        idx = x_fn(idx)
        if idx is None:
            return None

    # Apply Y rotations (yaw)
    y_fn = _rotate_y_left if y_rot >= 0 else _rotate_y_right
    for _ in range(abs(y_rot)):
        idx = y_fn(idx)
        if idx is None:
            return None

    # Apply Z rotations (roll)
    z_fn = _rotate_z_right if z_rot >= 0 else _rotate_z_left
    for _ in range(abs(z_rot)):
        idx = z_fn(idx)
        if idx is None:
            return None

    return idx


# -----------------------------------------------
# RANK ALL SETS FOR A SHOOTER'S SIGNATURE
# The core recommendation engine.
# Takes a shooter's measured rotation signature,
# applies it to every preset set, computes what
# totals result, and returns a ranked list.
# -----------------------------------------------

def rank_sets_for_signature(left_x, left_y, left_z, right_x, right_y, right_z, target="srr"):
    """
    Rank all preset dice sets for a specific shooter's rotation signature.

    Args:
        left_x/y/z:  Modal rotation values for the left die
        right_x/y/z: Modal rotation values for the right die
        target:       Betting goal — srr / 6_8 / 5_9 / 4_10 / all_box / come_out

    Returns:
        List of dicts, sorted best-to-worst, each containing:
        - name, phase, score, sevens, target_hits, distribution, reason
    """
    from collections import Counter

    # Default any None values to 0 (no rotation)
    lx = left_x  or 0
    ly = left_y  or 0
    lz = left_z  or 0
    rx = right_x or 0
    ry = right_y or 0
    rz = right_z or 0

    results = []

    for s in PRESET_SETS:
        # Get starting orientation index for each die
        l_start = TOP_FRONT_TO_IDX.get((s["lt"], s["lf"]))
        r_start = TOP_FRONT_TO_IDX.get((s["rt"], s["rf"]))
        if l_start is None or r_start is None:
            continue

        # Apply the shooter's rotation signature to each die
        l_end = apply_rotations(l_start, lx, ly, lz)
        r_end = apply_rotations(r_start, rx, ry, rz)
        if l_end is None or r_end is None:
            continue

        # Get the resulting orientations
        l_orient = ORIENTATIONS[l_end]  # (top, front, right, bottom, back, left)
        r_orient = ORIENTATIONS[r_end]

        # On-axis faces: top, front, bottom, back (indices 0,1,3,4)
        l_axis = (l_orient[0], l_orient[1], l_orient[3], l_orient[4])
        r_axis = (r_orient[0], r_orient[1], r_orient[3], r_orient[4])

        # Compute all 16 on-axis totals
        totals = []
        for lf in l_axis:
            for rf in r_axis:
                totals.append(lf + rf)

        dist = Counter(totals)
        sevens = dist.get(7, 0)

        # Count target hits based on goal
        target_map = {
            "come_out": [7],
            "6_8":      [6, 8],
            "5_9":      [5, 9],
            "4_10":     [4, 10],
            "all_box":  [4, 5, 6, 8, 9, 10],
            "srr":      [4, 5, 6, 8, 9, 10],  # SRR = all box numbers
        }
        target_nums = target_map.get(target, target_map["srr"])
        target_hits = sum(dist.get(n, 0) for n in target_nums)

        # Score the set: maximize target hits, minimize sevens
        # For come_out, we WANT sevens, so flip the logic
        if target == "come_out":
            # Come out: more sevens = better
            score = round((sevens / 16) * 100)
        else:
            # Point phase: more targets + fewer sevens = better
            # Weighted: 60% target hits, 40% seven avoidance
            target_pct = target_hits / 16
            seven_avoid = 1 - (sevens / 16)
            score = round((target_pct * 60) + (seven_avoid * 40))

        # Build the distribution breakdown for display
        breakdown = {}
        for n in range(2, 13):
            if dist.get(n, 0) > 0:
                breakdown[n] = dist[n]

        results.append({
            "name":        s["name"],
            "phase":       s["phase"],
            "score":       score,
            "sevens":      sevens,
            "seven_pct":   round(sevens / 16 * 100, 1),
            "target_hits": target_hits,
            "target_pct":  round(target_hits / 16 * 100, 1),
            "targets":     target_nums,
            "distribution": breakdown,
            "l_axis":      l_axis,
            "r_axis":      r_axis,
        })

    # Sort by score descending (best first)
    results.sort(key=lambda r: r["score"], reverse=True)

    # Add rank numbers
    for i, r in enumerate(results):
        r["rank"] = i + 1

    return results
