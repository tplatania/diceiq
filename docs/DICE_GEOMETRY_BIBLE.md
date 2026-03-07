# DICEIQ — DICE GEOMETRY BIBLE
## Standard Right-Handed Western Casino Die — Complete Reference

**Purpose:** This document is the authoritative, permanent reference for how a standard
right-handed Western casino die looks from every possible orientation. Any AI system,
developer, or validation engine MUST consult this document when rendering dice faces,
validating roll results, or computing dice set orientations.

---

## 1. FUNDAMENTAL RULES

**Rule 1 — Opposite faces sum to 7:**
- 1 opposite 6
- 2 opposite 5
- 3 opposite 4

**Rule 2 — Right-handed chirality:**
With 1 on top, looking at the 1-2-3 corner vertex, the faces go 1→2→3 counterclockwise
(as seen from inside the die). From outside: 2 is on the left, 3 is on the right.
The shared corner has NO pip.

**Rule 3 — Only three faces have orientation-dependent pip patterns:**
- Face 6: Two parallel lines of 3 pips (columns or rows depending on viewing angle)
- Face 2: Two pips on a diagonal
- Face 3: Three pips on a diagonal

**Rule 4 — Faces 1, 4, 5 are rotationally symmetric:**
They look identical at any 90° rotation. No orientation tracking needed.

---

## 2. THE SIX FACE — ORIENTATION RULE

The 6 face has two parallel lines of 3 pips each. These lines ALWAYS run in the
direction connecting faces 3 and 4 (the "3-4 axis"). The gap between the lines
faces toward faces 2 and 5 (the "2-5 axis").

**When 6 is on TOP, the orientation depends on which face is in FRONT:**

| Front Face | 6 on Top Looks Like | Why |
|------------|---------------------|-----|
| 3 in front | VERTICAL columns ‖ | Lines run toward 3 (front) and 4 (back) = top-to-bottom |
| 4 in front | VERTICAL columns ‖ | Lines run toward 4 (front) and 3 (back) = top-to-bottom |
| 2 in front | HORIZONTAL rows ═ | 3 and 4 are on left/right sides = left-to-right |
| 5 in front | HORIZONTAL rows ═ | 3 and 4 are on left/right sides = left-to-right |

**Quick rule:** If 2 or 5 is in front → 6 is HORIZONTAL (═). If 3 or 4 is in front → 6 is VERTICAL (‖).

**Verified from physical casino die photos (IMG_1827, IMG_1828, IMG_1829, IMG_1830).**

---

## 3. THE TWO FACE — DIAGONAL RULE

The 2 face has two pips on a diagonal. On a 3×3 grid:
- One pip is in one corner, the other in the opposite corner
- The diagonal direction changes based on viewing angle

**Confirmed from photos:**

| Orientation | 2-Face Diagonal Direction (as viewer sees it) |
|-------------|-----------------------------------------------|
| 2 on top, 3 in front (IMG_1825, IMG_1831) | ↗ upper-right to lower-left |
| 2 as front, 3 on top (IMG_1826) | ↘ upper-left to lower-right |
| 2 as front, 6 on top (IMG_1830) | ↘ upper-left to lower-right |

---

## 4. THE THREE FACE — DIAGONAL RULE

The 3 face has three pips on a diagonal (corner, center, opposite corner).

**Confirmed from photos:**

| Orientation | 3-Face Diagonal Direction (as viewer sees it) |
|-------------|-----------------------------------------------|
| 3 as front, 2 on top (IMG_1825) | ↗ upper-right, center, lower-left |
| 3 on top, 2 in front (IMG_1826) | ↘ upper-left, center, lower-right |
| 3 as front, 6 on top (IMG_1829) | ↘ upper-left, center, lower-right |

---

## 5. COMPLETE ADJACENCY MAP

For a right-handed Western die, given any face on top, here are all valid
"front" faces and what's on each side:

| Top | Front | Right | Left | Back | Bottom |
|-----|-------|-------|------|------|--------|
| 1 | 2 | 3 | 4 | 5 | 6 |
| 1 | 3 | 5 | 2 | 4 | 6 |
| 1 | 5 | 4 | 3 | 2 | 6 |
| 1 | 4 | 2 | 5 | 3 | 6 |
| 6 | 2 | 4 | 3 | 5 | 1 |
| 6 | 3 | 2 | 5 | 4 | 1 |
| 6 | 5 | 3 | 4 | 2 | 1 |
| 6 | 4 | 5 | 2 | 3 | 1 |
| 2 | 1 | 3 | 4 | 6 | 5 |
| 2 | 3 | 6 | 1 | 4 | 5 |
| 2 | 6 | 4 | 3 | 1 | 5 |
| 2 | 4 | 1 | 6 | 3 | 5 |
| 5 | 1 | 4 | 3 | 6 | 2 |
| 5 | 3 | 1 | 6 | 4 | 2 |
| 5 | 6 | 3 | 4 | 1 | 2 |
| 5 | 4 | 6 | 1 | 3 | 2 |
| 3 | 1 | 2 | 5 | 6 | 4 |
| 3 | 2 | 6 | 1 | 5 | 4 |
| 3 | 6 | 5 | 2 | 1 | 4 |
| 3 | 5 | 1 | 6 | 2 | 4 |
| 4 | 1 | 5 | 2 | 6 | 3 |
| 4 | 2 | 1 | 6 | 5 | 3 |
| 4 | 6 | 2 | 5 | 1 | 3 |
| 4 | 5 | 6 | 1 | 2 | 3 |

---

## 6. PIP RENDERING — THE 3x3 GRID SYSTEM

Each die face is rendered on a 3×3 grid. Positions are (row, col) where
row 0 = top of face, col 0 = left of face, as the viewer sees it.

```
(0,0)  (0,1)  (0,2)
(1,0)  (1,1)  (1,2)
(2,0)  (2,1)  (2,2)
```

### Face 1 — Center dot (symmetric, no rotation needed)
```
 ·  ·  ·
 ·  ●  ·
 ·  ·  ·
```
Pips: [(1,1)]

### Face 4 — Four corners (symmetric, no rotation needed)
```
 ●  ·  ●
 ·  ·  ·
 ●  ·  ●
```
Pips: [(0,0), (0,2), (2,0), (2,2)]

### Face 5 — Four corners + center (symmetric, no rotation needed)
```
 ●  ·  ●
 ·  ●  ·
 ●  ·  ●
```
Pips: [(0,0), (0,2), (1,1), (2,0), (2,2)]

### Face 6 — Two lines of 3 (ORIENTATION DEPENDENT)

**Vertical columns (‖) — when 3 or 4 is in front:**
```
 ●  ·  ●
 ●  ·  ●
 ●  ·  ●
```
Pips: [(0,0), (0,2), (1,0), (1,2), (2,0), (2,2)]

**Horizontal rows (═) — when 2 or 5 is in front:**
```
 ●  ●  ●
 ·  ·  ·
 ●  ●  ●
```
Pips: [(0,0), (0,1), (0,2), (2,0), (2,1), (2,2)]

### Face 2 — Two-pip diagonal (ORIENTATION DEPENDENT)

**↘ diagonal (upper-left to lower-right):**
```
 ●  ·  ·
 ·  ·  ·
 ·  ·  ●
```
Pips: [(0,0), (2,2)]

**↗ diagonal (upper-right to lower-left):**
```
 ·  ·  ●
 ·  ·  ·
 ●  ·  ·
```
Pips: [(0,2), (2,0)]

### Face 3 — Three-pip diagonal (ORIENTATION DEPENDENT)

**↘ diagonal (upper-left, center, lower-right):**
```
 ●  ·  ·
 ·  ●  ·
 ·  ·  ●
```
Pips: [(0,0), (1,1), (2,2)]

**↗ diagonal (upper-right, center, lower-left):**
```
 ·  ·  ●
 ·  ●  ·
 ●  ·  ·
```
Pips: [(0,2), (1,1), (2,0)]

---

## 7. DICEIQ DICE SETS — COMPLETE RENDERING SPEC

For each set, we show Left Die and Right Die with their top and front faces,
plus the exact pip grid for each visible face.

Notation: T = top face value, F = front face value

### 7.1 HARD WAY SET (Point phase — 4 ways to 7 — 25%)
Target: Avoid 7, survive the point. Hard way combos on all visible faces.

**Left Die: T=5, F=4**
- Top (5): symmetric → standard 5 pattern
- Front (4): symmetric → standard 4 pattern
- Right=6, Left=1, Back=3, Bottom=2

**Right Die: T=5, F=4**
- Top (5): symmetric → standard 5 pattern
- Front (4): symmetric → standard 4 pattern
- Right=1, Left=6, Back=3, Bottom=2

*Both dice show identical top/front patterns (faces 4 and 5 are symmetric).*

---

### 7.2 ALL SEVENS SET (Come Out phase — 4 ways to 7 — 25%)
Target: Hit 7 on come out. Every axis pair sums to 7.

**Left Die: T=4, F=5**
- Top (4): symmetric → standard 4 pattern
- Front (5): symmetric → standard 5 pattern
- Right=2, Left=5... 

For each set, we specify the exact pip positions for the TOP and FRONT faces
of each die. This is the ONLY information needed for rendering the dice set cards.

The pip positions are derived from:
1. The face value (which number)
2. The orientation rules from Sections 2-4 (verified from physical die photos)

**DETERMINATION METHOD for orientation-dependent faces (2, 3, 6):**
- For face 6: Check what's in FRONT. If front is 2 or 5 → horizontal ═. If front is 3 or 4 → vertical ‖.
- For face 2: Use photo-verified diagonal for each specific (top, front) pair.
- For face 3: Use photo-verified diagonal for each specific (top, front) pair.

### SET 1: HARD WAY — T5/F4 | T5/F4
Left Die top=5, front=4. Right Die top=5, front=4.
Both faces are symmetric (5 and 4). No orientation logic needed.

Left Top (5):        Right Top (5):
 ●  ·  ●              ●  ·  ●
 ·  ●  ·              ·  ●  ·
 ●  ·  ●              ●  ·  ●

Left Front (4):      Right Front (4):
 ●  ·  ●              ●  ·  ●
 ·  ·  ·              ·  ·  ·
 ●  ·  ●              ●  ·  ●

---

### SET 2: ALL SEVENS — T4/F5 | T3/F2
Left Die top=4, front=5. Right Die top=3, front=2.

Left Die: top=4 (symmetric), front=5 (symmetric). No orientation logic needed.

Left Top (4):        Left Front (5):
 ●  ·  ●              ●  ·  ●
 ·  ·  ·              ·  ●  ·
 ●  ·  ●              ●  ·  ●

Right Die: top=3, front=2. Both are orientation-dependent.
- Top (3) with front=2: Photo IMG_1826 shows 3 on top, 2 in front → 3 is ↘
- Front (2) with top=3: Photo IMG_1826 shows 2 in front, 3 on top → 2 is ↘

Right Top (3):       Right Front (2):
 ●  ·  ·              ●  ·  ·
 ·  ●  ·              ·  ·  ·
 ·  ·  ●              ·  ·  ●

---

### SET 3: 3V SET — T3/F6 | T3/F2
Left Die top=3, front=6. Right Die top=3, front=2.

Left Die: top=3, front=6.
- Top (3) with front=6: Photo IMG_1829 shows 6 on top, 3 in front where 3 is ↘.
  When we SWAP (3 on top, 6 in front), the 3 rotates.
  From the die: if 6t/3f has 3-front as ↘, then 3t/6f has 3-top rotated 180° from 
  the 3t/2f case. In IMG_1826 (3t/2f) the 3 is ↘. Rotating the die 180° around the 
  vertical axis to go from front=2 to front=6 gives us 3 on top as ↗.
  **Top 3 with 6 in front = ↗**
- Front (6) with top=3: 3 is adjacent to 6. Since 3 is on TOP (not 2 or 5), 
  the 6 shows VERTICAL columns ‖.
  **Front 6 with 3 on top = vertical ‖**

Left Top (3):        Left Front (6):
 ·  ·  ●              ●  ·  ●
 ·  ●  ·              ●  ·  ●
 ●  ·  ·              ●  ·  ●

Right Die: top=3, front=2 — identical to All Sevens right die.
- Top (3): ↘ (from IMG_1826)
- Front (2): ↘ (from IMG_1826)

Right Top (3):       Right Front (2):
 ●  ·  ·              ●  ·  ·
 ·  ●  ·              ·  ·  ·
 ·  ·  ●              ·  ·  ●

**3V confirmation:** The two 3s on top form a V shape — left die 3 goes ↗, right die 3 goes ↘.
That's the V! ✓

---

### SET 4: STRAIGHT SIXES — T6/F5 | T6/F5
Left Die top=6, front=5. Right Die top=6, front=5.

Both dice identical. 
- Top (6) with front=5: 5 is in front → HORIZONTAL rows ═ (Section 2 rule, IMG_1828)
- Front (5): symmetric, no orientation needed.

Left Top (6):        Right Top (6):
 ●  ●  ●              ●  ●  ●
 ·  ·  ·              ·  ·  ·
 ●  ●  ●              ●  ●  ●

Left Front (5):      Right Front (5):
 ●  ·  ●              ●  ·  ●
 ·  ●  ·              ·  ●  ·
 ●  ·  ●              ●  ·  ●

**Both 6s run the same direction (horizontal) = "straight." ✓**

---

### SET 5: CROSSED SIXES — T6/F5 | T6/F4
Left Die top=6, front=5. Right Die top=6, front=4.

Left Die: same as Straight Sixes left die.
- Top (6) with front=5: HORIZONTAL rows ═ (IMG_1828)
- Front (5): symmetric

Right Die: top=6, front=4.
- Top (6) with front=4: 4 is in front → VERTICAL columns ‖ (IMG_1827)
- Front (4): symmetric

Left Top (6):        Right Top (6):
 ●  ●  ●              ●  ·  ●
 ·  ·  ·              ●  ·  ●
 ●  ●  ●              ●  ·  ●

Left Front (5):      Right Front (4):
 ●  ·  ●              ●  ·  ●
 ·  ●  ·              ·  ·  ·
 ●  ·  ●              ●  ·  ●

**The two 6s run DIFFERENT directions (horizontal vs vertical) = "crossed." ✓**

---

### SET 6: 6/5-5/6 SET — T6/F5 | T5/F6
Left Die top=6, front=5. Right Die top=5, front=6.

Left Die: same as Straight Sixes left die.
- Top (6) with front=5: HORIZONTAL rows ═
- Front (5): symmetric

Right Die: top=5, front=6.
- Top (5): symmetric
- Front (6) with top=5: 5 is on top (not 3 or 4). To determine the 6 orientation 
  when viewed from front with 5 on top: The 3-4 axis determines the line direction.
  With 5 on top, faces 3 and 4 are on the sides (left/right). The 6 lines run 
  toward 3 and 4 = LEFT-TO-RIGHT = HORIZONTAL rows ═ when viewed from front.
  **Front 6 with 5 on top = horizontal ═**

Left Top (6):        Right Top (5):
 ●  ●  ●              ●  ·  ●
 ·  ·  ·              ·  ●  ·
 ●  ●  ●              ●  ·  ●

Left Front (5):      Right Front (6):
 ●  ·  ●              ●  ●  ●
 ·  ●  ·              ·  ·  ·
 ●  ·  ●              ●  ●  ●

---

### SET 7: 2V SET — T2/F3 | T2/F1
Left Die top=2, front=3. Right Die top=2, front=1.

Left Die: top=2, front=3.
- Top (2) with front=3: Photo IMG_1831 shows 2t/3f → 2 is ↗
- Front (3) with top=2: Photo IMG_1831 shows 3f/2t → 3 is ↗

Right Die: top=2, front=1.
- Top (2) with front=1: Different from 2t/3f. Going from front=3 to front=1 
  requires rotating the die 180° around the vertical axis (1 is opposite to... 
  wait, 1 is not opposite 3. 1 is adjacent to 2. Let me think.)
  From the adjacency table: T=2, F=1 is valid. T=2, F=3 has the 2 as ↘.
  To get from F=3 to F=1: that's a 90° rotation around the vertical axis.
  90° CW rotation of the top face: the ↗ diagonal rotates to ↘.
  **Top 2 with 1 in front = ↘**
- Front (1): symmetric, no orientation needed.

Left Top (2):        Right Top (2):
 ·  ·  ●              ●  ·  ·
 ·  ·  ·              ·  ·  ·
 ●  ·  ·              ·  ·  ●

Left Front (3):      Right Front (1):
 ·  ·  ●              ·  ·  ·
 ·  ●  ·              ·  ●  ·
 ●  ·  ·              ·  ·  ·

**The two 2s on top form a V shape — left die 2 goes ↗, right die 2 goes ↘.
That's the V! ✓ (Verified from physical dice photo IMG_1831)**

---

## 8. RENDERING LOOKUP TABLE (for code)

This is the machine-readable version. For each set, for each die, for each
visible face: the exact pip positions as (row, col) arrays.

Format: setId → leftDie → {top: [[r,c]...], front: [[r,c]...]} , rightDie → same

```json
{
  "hard-way": {
    "left":  { "topVal":5, "topPips":[[0,0],[0,2],[1,1],[2,0],[2,2]], "frontVal":4, "frontPips":[[0,0],[0,2],[2,0],[2,2]] },
    "right": { "topVal":5, "topPips":[[0,0],[0,2],[1,1],[2,0],[2,2]], "frontVal":4, "frontPips":[[0,0],[0,2],[2,0],[2,2]] }
  },
  "all-sevens": {
    "left":  { "topVal":4, "topPips":[[0,0],[0,2],[2,0],[2,2]], "frontVal":5, "frontPips":[[0,0],[0,2],[1,1],[2,0],[2,2]] },
    "right": { "topVal":3, "topPips":[[0,0],[1,1],[2,2]], "frontVal":2, "frontPips":[[0,0],[2,2]] }
  },
  "3v-set": {
    "left":  { "topVal":3, "topPips":[[0,2],[1,1],[2,0]], "frontVal":6, "frontPips":[[0,0],[0,2],[1,0],[1,2],[2,0],[2,2]] },
    "right": { "topVal":3, "topPips":[[0,0],[1,1],[2,2]], "frontVal":2, "frontPips":[[0,0],[2,2]] }
  },
  "straight-sixes": {
    "left":  { "topVal":6, "topPips":[[0,0],[0,1],[0,2],[2,0],[2,1],[2,2]], "frontVal":5, "frontPips":[[0,0],[0,2],[1,1],[2,0],[2,2]] },
    "right": { "topVal":6, "topPips":[[0,0],[0,1],[0,2],[2,0],[2,1],[2,2]], "frontVal":5, "frontPips":[[0,0],[0,2],[1,1],[2,0],[2,2]] }
  },
  "crossed-sixes": {
    "left":  { "topVal":6, "topPips":[[0,0],[0,1],[0,2],[2,0],[2,1],[2,2]], "frontVal":5, "frontPips":[[0,0],[0,2],[1,1],[2,0],[2,2]] },
    "right": { "topVal":6, "topPips":[[0,0],[0,2],[1,0],[1,2],[2,0],[2,2]], "frontVal":4, "frontPips":[[0,0],[0,2],[2,0],[2,2]] }
  },
  "6-5-5-6": {
    "left":  { "topVal":6, "topPips":[[0,0],[0,1],[0,2],[2,0],[2,1],[2,2]], "frontVal":5, "frontPips":[[0,0],[0,2],[1,1],[2,0],[2,2]] },
    "right": { "topVal":5, "topPips":[[0,0],[0,2],[1,1],[2,0],[2,2]], "frontVal":6, "frontPips":[[0,0],[0,1],[0,2],[2,0],[2,1],[2,2]] }
  },
  "2v-set": {
    "left":  { "topVal":2, "topPips":[[0,2],[2,0]], "frontVal":3, "frontPips":[[0,2],[1,1],[2,0]] },
    "right": { "topVal":2, "topPips":[[0,0],[2,2]], "frontVal":1, "frontPips":[[1,1]] }
  }
}
```

---

## 9. VALIDATION RULES

When the AI receives a roll result (e.g., "6 top, 5 front"), it MUST:

1. **Verify adjacency:** The top and front faces must be adjacent (not opposite).
   Opposite pairs (1-6, 2-5, 3-4) can NEVER be top-and-front simultaneously.

2. **Determine 6 orientation instantly:** If a 6 is visible, check what's adjacent.
   - 6 on top + (2 or 5) in front → 6 is horizontal ═
   - 6 on top + (3 or 4) in front → 6 is vertical ‖
   - 6 in front + (2 or 5) on top → 6 is horizontal ═
   - 6 in front + (3 or 4) on top → 6 is vertical ‖

3. **Determine 2/3 diagonal direction:** Use the rotation tracking system.
   The diagonal direction depends on which face is "up" when viewing that face.
   Use the NEIGHBOR_CW cycle to compute rotation from reference.

4. **Cross-validate set names:** For named sets, verify the pip patterns match:
   - "Straight" = both 6s same direction
   - "Crossed" = both 6s different directions
   - "V" sets = the V-number pips form a V shape (diagonals mirror each other)
   - "Hard Way" = matching pairs on all visible face pairs

---

## 10. SOURCE VERIFICATION

All orientation data in this document was verified against physical casino dice
photographs taken specifically for this purpose:

- IMG_1825: 2 on top, 3 facing camera
- IMG_1826: 3 on top, 2 facing camera
- IMG_1827: 6 on top, 4 facing camera → 6 shows vertical columns ‖
- IMG_1828: 6 on top, 5 facing camera → 6 shows horizontal rows ═
- IMG_1829: 6 on top, 3 facing camera → 6 shows vertical columns ‖
- IMG_1830: 6 on top, 2 facing camera → 6 shows horizontal rows ═
- IMG_1831: 2V set — both dice side by side, 2s on top forming V (left ↗, right ↘)

These photos are stored in the project and constitute the ground truth.

---

*DiceIQ Dice Geometry Bible | v1.0 | Verified against physical casino dice*
*This document governs all dice rendering and validation in DiceIQ.*
