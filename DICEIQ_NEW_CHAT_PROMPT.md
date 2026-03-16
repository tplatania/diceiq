# DICEIQ SESSION HANDOFF — March 10, 2026

## What happened this session

### 1. Custom Sets — Orientation-Aware Dice Rendering
Built the `getOrientedPips()` engine and wired it into the custom dice sets page so user-created sets show the same visual dice face previews as the presets.

**New file:** `frontend/app/components/DiceFaceRenderer.tsx`
- `getOrientedPips(faceValue, position, adjacent)` — computes correct pip positions for any (top, front) pair
- `DiceFace` — renders a single die face from pip positions
- `DiceSetPreviewDynamic` — renders 2×2 grid (top+front for both dice)
- All orientation rules from DICE_GEOMETRY_BIBLE.md implemented
- Fixed face 3 orientation bug: front=6 produces ↗ not ↘ (needed for V shape)
- Verified against all 7 hardcoded presets — ALL PASS

**Updated:** `frontend/app/session/setup/custom-sets/page.tsx`
- Dice preview on saved custom set cards (matches preset card layout)
- Live dice preview in creation form (appears when all 4 faces selected)
- Smart face picker: opposite faces greyed out (can't pick 1 top + 6 front)
- Auto-clears paired face if changing selection makes it invalid
- Fixed hydration error (button nested in button → changed card to div)
- Updated 7s label to match preset format

### 2. Confirmed All 7 Preset Dice Sets Are Correct
Reviewed every preset against the Bible — face values AND pip orientations all verified:
- Hard Way: T5/F4 | T5/F4 ✓
- All Sevens: T4/F5 | T3/F2 ✓
- 3V Set: T3/F6 | T3/F2 ✓ (confirmed from Tom's photos IMG_1841/1842 — both 3s on top forming V)
- Straight Sixes: T6/F5 | T6/F5 ✓
- Crossed Sixes: T6/F5 | T6/F4 ✓
- 6/5-5/6: T6/F5 | T5/F6 ✓
- 2V Set: T2/F3 | T2/F1 ✓

### 3. The 576 Matrix — Complete Dice Set Analysis
Computed all 576 possible dice set combinations (24 orientations × 24) against every box number. Key findings:

**Our presets already contain the optimal set for every box number:**

| Target | Best Set | Hits/16 | 7s/16 | Ratio |
|--------|----------|---------|-------|-------|
| 4      | 2V Set   | 2 (13%) | 2     | 1.00  |
| 5      | 3V Set   | 2 (13%) | 2     | 1.00  |
| 6      | 3V Set   | 3 (19%) | 2     | 1.50  |
| 8      | 3V Set   | 3 (19%) | 2     | 1.50  |
| 9      | 3V Set   | 2 (13%) | 2     | 1.00  |
| 10     | 2V Set   | 2 (13%) | 2     | 1.00  |

**3V is the king** for point phase (optimal for 5, 6, 8, 9).
**2V owns the outsides** (4 and 10).
**Hard Way carries double the seven exposure** (4 sevens vs 2) for same or fewer hits — the math proves 3V and 2V are superior.

### 4. STA (Small/Tall/All) Strategy Discovery
Analyzed optimal sets for the Small/Tall/All betting strategy:

**Crossed Sixes is the optimal come-out set for STA play:**
- Only 2 sevens on-axis (protects STA bets)
- Covers ALL 10 non-seven numbers (2,3,4,5,6,8,9,10,11,12)
- Includes both 2 AND 12 (hardest STA numbers)
- Has a yo 11 for pass line wins without killing STA

**STA Drill Cheat Sheet — optimal set for each number:**

| Need | Set | Hits/16 | 7s/16 |
|------|-----|---------|-------|
| 2    | Crossed 6s | 1 | 2 |
| 3    | Straight 6s | 2 | 4 |
| 4    | 2V Set | 2 | 2 |
| 5    | 3V Set | 2 | 2 |
| 6    | 3V Set | 3 | 2 |
| 8    | 3V Set | 3 | 2 |
| 9    | 3V Set | 2 | 2 |
| 10   | 2V Set | 2 | 2 |
| 11   | Straight 6s | 2 | 4 |
| 12   | Crossed 6s | 1 | 2 |

Only 4 sets needed to cover all 10 STA numbers. Beautiful symmetry — low mirrors high.

### 5. Reviewed All NASA-Level Docs
Read through the complete doc set on the DT machine (D:/diceiq/):
- **Physics Bible v1.1** — 12 sections covering throw mechanics, rotation axes, diagnostics, glide path physics, deceleration runway, era system
- **Architecture Blueprint** — 12 sections covering full tech stack, data model, API endpoints, ElevenLabs config, skill progression, bet strategy engine, deployment
- **Section 15 Addendum** — The Rotation Analysis & Set Recommendation Engine. THIS is where the drift compensation logic lives. Key quote: "It does not tell the shooter to change how they throw. It finds the set that meets them where they are."

## Pushed to GitHub
Commit: "Add orientation-aware dice rendering for custom sets" — ec682ec

## WHAT TO BUILD NEXT (in priority order)

### Immediate — Frontend
1. **getOrientedPips() could replace hardcoded SET_PIPS** in dice-set/page.tsx too (consolidation, not urgent)

### Immediate — Backend
2. **ElevenLabs tool endpoints** (checklist items 37-40) — gives the voice coach "eyes"
3. **Deploy to Cloud Run** — then register tool URLs in ElevenLabs dashboard

### Medium Term
4. **576 Matrix integration** — bake the STA drill cheat sheet and optimal set data into the app
5. **Set Recommendation Engine** (Section 15.7) — uses shooter's rotation signature to recommend compensated starting positions
6. **Betting Strategy Simulator** — STA practice mode, come-out vs point set switching

### Key Insight from Tom
The app is 90% for offsite practice. At home, shooters can take their time and set dice to a specific configuration for each throw. This enables the STA Drill concept — practice hitting each number individually with the mathematically optimal set. Nobody in the dice control community teaches this.

The drift compensation concept: if a shooter's right die consistently rotates one extra pitch forward, don't fight it — pre-compensate the starting position so the natural rotation lands on the target. "Zeroing the rifle scope."

## FILE LOCATIONS

### Mac (via DC on Mac)
- Project: `/Users/macdaddy/Development/diceiq/`
- Handoff: `/Users/macdaddy/Development/DICEIQ_NEW_CHAT_PROMPT.md`

### DT Windows (via DC on DT)
- Project: `D:/diceiq/`
- Handoff: `D:/diceiq/DICEIQ_NEW_CHAT_PROMPT.md`

### Key Docs (DT)
- Physics Bible: `D:/diceiq/DiceIQ_Physics_Bible_v1.1.docx`
- Architecture Blueprint: `D:/diceiq/DiceIQ_Architecture_Blueprint.docx`
- Section 15 Addendum: `D:/diceiq/DiceIQ_Section15_Addendum.docx`
- Dice Geometry Bible: `D:/diceiq/docs/DICE_GEOMETRY_BIBLE.md` (also in memory)
- Master Checklist: `D:/diceiq/DiceIQ_Master_Checklist_v1.docx`

## SYNTAX VERIFICATION PATTERN
Mac: `cd /Users/macdaddy/Development/diceiq && python3 -m py_compile backend/[file].py && echo ALL OK`
DT: `cd D:\diceiq && python -m py_compile backend/[file].py && echo ALL OK`
