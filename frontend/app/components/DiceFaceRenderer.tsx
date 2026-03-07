// ═══════════════════════════════════════════════════════════════
// DiceIQ — Shared Dice Face Rendering Components
// Orientation-aware pip rendering based on DICE_GEOMETRY_BIBLE.md
// Verified against physical casino dice photos (IMG_1825–1842)
// ═══════════════════════════════════════════════════════════════

import React from "react";

// ── Orientation Rules ──────────────────────────────────────────
// Face 1, 4, 5: Rotationally symmetric — always the same
// Face 6: horizontal ═ when adjacent is 2 or 5, vertical ‖ when adjacent is 3 or 4
// Face 2: diagonal depends on viewing context (top vs front, and neighbor)
// Face 3: diagonal depends on viewing context (top vs front, and neighbor)
// ───────────────────────────────────────────────────────────────

type PipPosition = [number, number];

// Static pip positions for symmetric faces
const FACE_1: PipPosition[] = [[1,1]];
const FACE_4: PipPosition[] = [[0,0],[0,2],[2,0],[2,2]];
const FACE_5: PipPosition[] = [[0,0],[0,2],[1,1],[2,0],[2,2]];

// Face 6 variants
const FACE_6_VERTICAL: PipPosition[]   = [[0,0],[0,2],[1,0],[1,2],[2,0],[2,2]];
const FACE_6_HORIZONTAL: PipPosition[] = [[0,0],[0,1],[0,2],[2,0],[2,1],[2,2]];

// Face 2 variants
const FACE_2_NE: PipPosition[] = [[0,2],[2,0]]; // ↗ diagonal
const FACE_2_SE: PipPosition[] = [[0,0],[2,2]]; // ↘ diagonal

// Face 3 variants
const FACE_3_NE: PipPosition[] = [[0,2],[1,1],[2,0]]; // ↗ diagonal
const FACE_3_SE: PipPosition[] = [[0,0],[1,1],[2,2]]; // ↘ diagonal

/**
 * getOrientedPips — the core orientation engine
 *
 * Given a face value and its context (is it on top or front, and what's the
 * adjacent face), returns the correct pip positions on a 3×3 grid.
 */
export function getOrientedPips(
  faceValue: number,
  position: "top" | "front",
  adjacent: number
): PipPosition[] {
  if (faceValue === 1) return FACE_1;
  if (faceValue === 4) return FACE_4;
  if (faceValue === 5) return FACE_5;

  if (faceValue === 6) {
    if (adjacent === 2 || adjacent === 5) return FACE_6_HORIZONTAL;
    if (adjacent === 3 || adjacent === 4) return FACE_6_VERTICAL;
    return FACE_6_VERTICAL;
  }

  // Face 2: on TOP diagonal depends on front; in FRONT always ↘
  if (faceValue === 2) {
    if (position === "front") return FACE_2_SE;
    if (adjacent === 3 || adjacent === 6) return FACE_2_NE;
    if (adjacent === 1 || adjacent === 4) return FACE_2_SE;
    return FACE_2_SE;
  }

  // Face 3: on TOP and in FRONT both context-dependent
  // 3 on TOP:  front=2 → ↘, front=6 → ↗, front=1 → ↗, front=5 → ↗
  // 3 in FRONT: top=2 → ↗, top=5 → ↗, top=6 → ↘, top=1 → ↘
  if (faceValue === 3) {
    if (position === "top") {
      if (adjacent === 2) return FACE_3_SE; // ↘ only when front=2
      return FACE_3_NE; // ↗ for front=6, 1, 5
    }
    if (adjacent === 2 || adjacent === 5) return FACE_3_NE;
    if (adjacent === 6 || adjacent === 1) return FACE_3_SE;
    return FACE_3_SE;
  }

  return FACE_1;
}

/** DiceFace — renders a single die face with pip positions */
export function DiceFace({ pips, size = 22, isTop = true }: {
  pips: PipPosition[];
  size?: number;
  isTop?: boolean;
}) {
  const padding = size * 0.15;
  const dotSize = size * 0.23;
  const cellSize = (size - padding * 2) / 3;
  return (
    <div style={{
      width: size, height: size, borderRadius: size * 0.15,
      background: isTop ? "rgba(30,111,217,0.15)" : "rgba(30,111,217,0.06)",
      border: `1px solid ${isTop ? "rgba(30,111,217,0.4)" : "rgba(30,111,217,0.15)"}`,
      position: "relative" as const, flexShrink: 0,
    }}>
      {pips.map(([row, col], i) => (
        <div key={i} style={{
          position: "absolute" as const,
          width: dotSize, height: dotSize, borderRadius: "50%",
          background: isTop ? "#4DA3FF" : "rgba(77,163,255,0.4)",
          boxShadow: isTop ? "0 0 3px rgba(77,163,255,0.5)" : "none",
          left: padding + col * cellSize + (cellSize - dotSize) / 2,
          top: padding + row * cellSize + (cellSize - dotSize) / 2,
        }} />
      ))}
    </div>
  );
}

/** DiceSetPreviewDynamic — 2×2 grid showing top+front for both dice */
export function DiceSetPreviewDynamic({ leftTop, leftFront, rightTop, rightFront }: {
  leftTop: number;
  leftFront: number;
  rightTop: number;
  rightFront: number;
}) {
  const ltPips = getOrientedPips(leftTop, "top", leftFront);
  const lfPips = getOrientedPips(leftFront, "front", leftTop);
  const rtPips = getOrientedPips(rightTop, "top", rightFront);
  const rfPips = getOrientedPips(rightFront, "front", rightTop);

  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 2, flexShrink: 0 }}>
      <DiceFace pips={ltPips} size={22} isTop={true} />
      <DiceFace pips={rtPips} size={22} isTop={true} />
      <DiceFace pips={lfPips} size={18} isTop={false} />
      <DiceFace pips={rfPips} size={18} isTop={false} />
    </div>
  );
}
