"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense } from "react";
import ThemeToggle from "../../../components/ThemeToggle";

// Dot positions for each die face value (1-6) on a 3x3 grid
const DOT_POSITIONS: Record<number, [number, number][]> = {
  1: [[1, 1]],
  2: [[0, 2], [2, 0]],
  3: [[0, 2], [1, 1], [2, 0]],
  4: [[0, 0], [0, 2], [2, 0], [2, 2]],
  5: [[0, 0], [0, 2], [1, 1], [2, 0], [2, 2]],
  6: [[0, 0], [0, 2], [1, 0], [1, 2], [2, 0], [2, 2]],
};

function DiceFace({ value, size = 22, isTop = true }: { value: number; size?: number; isTop?: boolean }) {
  const dots = DOT_POSITIONS[value] || [];
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
      {dots.map(([row, col], i) => (
        <div key={i} style={{
          position: "absolute" as const, width: dotSize, height: dotSize, borderRadius: "50%",
          background: isTop ? "#4DA3FF" : "rgba(77,163,255,0.4)",
          boxShadow: isTop ? "0 0 3px rgba(77,163,255,0.5)" : "none",
          left: padding + col * cellSize + (cellSize - dotSize) / 2,
          top: padding + row * cellSize + (cellSize - dotSize) / 2,
        }} />
      ))}
    </div>
  );
}

function DiceSetPreview({ leftTop, leftFront, rightTop, rightFront }: {
  leftTop: number; leftFront: number; rightTop: number; rightFront: number;
}) {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 2, flexShrink: 0 }}>
      <DiceFace value={leftTop} size={22} isTop={true} />
      <DiceFace value={rightTop} size={22} isTop={true} />
      <DiceFace value={leftFront} size={18} isTop={false} />
      <DiceFace value={rightFront} size={18} isTop={false} />
    </div>
  );
}

const DICE_SETS = [
  { id: "all-sevens", name: "All Sevens", target: "Hit 7 on come out", phase: "Come Out", phaseColor: "#2ECC71", sevenWays: 4, sevenPct: "25%", leftTop: 4, leftFront: 5, rightTop: 3, rightFront: 2 },
  { id: "hard-way", name: "Hard Way", target: "Avoid 7, survive point", phase: "Point", phaseColor: "#1E6FD9", sevenWays: 4, sevenPct: "25%", leftTop: 4, leftFront: 5, rightTop: 4, rightFront: 5 },
  { id: "3v-set", name: "3V Set", target: "Hit 6 and 8", phase: "Point", phaseColor: "#1E6FD9", sevenWays: 2, sevenPct: "12%", leftTop: 3, leftFront: 2, rightTop: 3, rightFront: 6 },
  { id: "straight-sixes", name: "Straight Sixes", target: "Come out rolls", phase: "Come Out", phaseColor: "#2ECC71", sevenWays: 4, sevenPct: "25%", leftTop: 6, leftFront: 2, rightTop: 6, rightFront: 2 },
  { id: "crossed-sixes", name: "Crossed Sixes", target: "Outside numbers", phase: "Point", phaseColor: "#1E6FD9", sevenWays: 2, sevenPct: "12%", leftTop: 6, leftFront: 5, rightTop: 6, rightFront: 4 },
  { id: "6-5-5-6", name: "6/5-5/6 Set", target: "Come out ONLY", phase: "Come Out", phaseColor: "#2ECC71", sevenWays: 4, sevenPct: "25%", leftTop: 6, leftFront: 5, rightTop: 5, rightFront: 6 },
  { id: "2v-set", name: "2V Set", target: "Hit 4 and 10", phase: "Point", phaseColor: "#1E6FD9", sevenWays: 2, sevenPct: "12%", leftTop: 2, leftFront: 3, rightTop: 2, rightFront: 1 },
];

function DiceSetContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const mode = searchParams.get("mode") || "roll";
  const [selected, setSelected] = useState<string | null>(null);

  return (
    <main style={styles.page}>

      {/* ── Top Bar ── */}
      <div style={styles.topBar}>
        <button style={styles.backBtn}
          onClick={() => router.push("/session/setup")}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="15 18 9 12 15 6"/>
          </svg>
        </button>
        <span style={styles.stepLabel}>STEP 2 OF 3</span>
        <ThemeToggle />
      </div>

      {/* ── Header ── */}
      <div style={styles.header}>
        <h2 style={styles.title}>Select Dice Set</h2>
        <p style={styles.subtitle}>Which set are you throwing today?</p>
      </div>

      {/* ── Grid ── */}
      <div style={styles.grid}>
        {DICE_SETS.map((set) => (
          <button
            key={set.id}
            style={{
              ...styles.card,
              ...(selected === set.id ? styles.cardActive : {}),
            }}
            onClick={() => setSelected(set.id)}
          >
            {/* Phase badge */}
            <span style={{
              ...styles.phaseBadge,
              color: set.phaseColor,
              borderColor: set.phaseColor,
            }}>
              {set.phase}
            </span>

            {/* Name + dice row */}
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", width: "100%", gap: 4 }}>
              <div style={{ flex: 1, minWidth: 0 }}>
                <h3 style={styles.setName}>{set.name}</h3>
                <p style={styles.setTarget}>{set.target}</p>
              </div>
              <DiceSetPreview leftTop={set.leftTop} leftFront={set.leftFront} rightTop={set.rightTop} rightFront={set.rightFront} />
            </div>

            {/* Seven stats */}
            <div style={styles.setMeta}>
              <span style={styles.metaLabel}>7s</span>
              <span style={{
                ...styles.metaValue,
                color: set.sevenWays <= 2 ? "#2ECC71" : "#F39C12",
              }}>
                {set.sevenWays} ways · {set.sevenPct}
              </span>
            </div>

            {/* Selected indicator */}
            {selected === set.id && (
              <div style={styles.selectedDot} />
            )}
          </button>
        ))}

        {/* ── Custom Sets Card ── */}
        <button
          style={styles.card}
          onClick={() => router.push(`/session/setup/custom-sets?mode=${mode}`)}
        >
          <span style={{
            ...styles.phaseBadge,
            color: "#B8C4D0",
            borderColor: "#B8C4D0",
          }}>
            Custom
          </span>
          <h3 style={styles.setName}>Custom Sets</h3>
          <p style={styles.setTarget}>Create & manage your own sets</p>
          <div style={styles.setMeta}>
            <span style={styles.metaLabel}>7s</span>
            <span style={{ ...styles.metaValue, color: "var(--silver-mid)" }}>
              Calculated on save
            </span>
          </div>
        </button>

      </div>

      {/* ── Next Button ── */}
      <div style={styles.footer}>
        <button
          className="btn-primary"
          style={{
            ...styles.nextBtn,
            opacity: selected ? 1 : 0.4,
            cursor: selected ? "pointer" : "not-allowed",
          }}
          disabled={!selected}
          onClick={() => selected && router.push(
            `/session/setup/confirm?mode=${mode}&set=${selected}`
          )}
        >
          NEXT — CONFIRM & START
        </button>
      </div>

    </main>
  );
}

export default function DiceSetPage() {
  return (
    <Suspense>
      <DiceSetContent />
    </Suspense>
  );
}

const styles: Record<string, React.CSSProperties> = {
  page: {
    minHeight: "100dvh",
    maxHeight: "100dvh",
    overflow: "hidden",
    display: "flex",
    flexDirection: "column",
    padding: "12px 16px 16px",
    background: "var(--bg-primary)",
    maxWidth: "420px",
    margin: "0 auto",
    width: "100%",
    gap: "10px",
  },
  topBar: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    paddingTop: "8px",
  },
  backBtn: {
    background: "transparent",
    border: "1px solid var(--border)",
    borderRadius: "8px",
    width: "36px",
    height: "36px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    cursor: "pointer",
    color: "var(--text-muted)",
  },
  stepLabel: {
    fontSize: "0.65rem",
    color: "var(--text-muted)",
    letterSpacing: "0.15em",
    fontFamily: "var(--font-mono)",
  },
  header: {
    display: "flex",
    flexDirection: "column",
    gap: "2px",
  },
  title: {
    fontSize: "clamp(1.3rem, 4vw, 1.6rem)",
    fontFamily: "var(--font-display)",
    fontWeight: 700,
    letterSpacing: "0.08em",
    color: "var(--text-primary)",
  },
  subtitle: {
    fontSize: "0.78rem",
    color: "var(--text-muted)",
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "10px",
    flex: 1,
  },
  card: {
    display: "flex",
    flexDirection: "column",
    alignItems: "flex-start",
    gap: "4px",
    padding: "10px 10px",
    background: "var(--bg-surface)",
    border: "1px solid var(--border)",
    borderRadius: "10px",
    cursor: "pointer",
    textAlign: "left",
    transition: "all 0.2s ease",
    position: "relative",
    width: "100%",
    justifyContent: "flex-start",
  },
  cardActive: {
    border: "1px solid var(--blue-electric)",
    background: "rgba(30, 111, 217, 0.08)",
    boxShadow: "0 0 16px rgba(30, 111, 217, 0.2)",
  },
  phaseBadge: {
    fontSize: "0.55rem",
    letterSpacing: "0.08em",
    textTransform: "uppercase" as const,
    fontFamily: "var(--font-mono)",
    border: "1px solid",
    borderRadius: "4px",
    padding: "1px 5px",
  },
  setName: {
    fontSize: "0.95rem",
    fontFamily: "var(--font-display)",
    fontWeight: 600,
    letterSpacing: "0.03em",
    color: "var(--text-primary)",
    lineHeight: 1.2,
  },
  setTarget: {
    fontSize: "0.75rem",
    color: "var(--text-muted)",
    lineHeight: 1.3,
    flex: 1,
  },
  setMeta: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "1px",
    marginTop: "0px",
  },
  metaLabel: {
    fontSize: "0.6rem",
    color: "var(--text-muted)",
    letterSpacing: "0.08em",
    textTransform: "uppercase" as const,
    fontFamily: "var(--font-mono)",
  },
  metaValue: {
    fontSize: "0.78rem",
    fontWeight: 600,
    fontFamily: "var(--font-mono)",
  },
  selectedDot: {
    position: "absolute",
    top: "10px",
    right: "10px",
    width: "8px",
    height: "8px",
    borderRadius: "50%",
    background: "var(--blue-electric)",
    boxShadow: "0 0 6px rgba(30, 111, 217, 0.8)",
  },
  customCard: {
    display: "flex",
    flexDirection: "column" as const,
    alignItems: "center",
    justifyContent: "center",
    gap: "6px",
    padding: "10px",
    background: "transparent",
    border: "1px dashed var(--border-bright)",
    borderRadius: "10px",
    cursor: "pointer",
    textAlign: "center" as const,
    transition: "all 0.2s ease",
    width: "100%",
  },
  customIcon: {
    fontSize: "1.4rem",
    color: "var(--silver-mid)",
    lineHeight: 1,
  },
  customName: {
    fontSize: "0.85rem",
    fontFamily: "var(--font-display)",
    fontWeight: 600,
    color: "var(--silver-mid)",
    letterSpacing: "0.03em",
  },
  customDesc: {
    fontSize: "0.62rem",
    color: "var(--text-muted)",
    lineHeight: 1.3,
  },
  footer: {
    paddingTop: "2px",
  },
  nextBtn: {
    width: "100%",
    padding: "14px",
    fontSize: "0.9rem",
    letterSpacing: "0.12em",
    borderRadius: "12px",
    transition: "opacity 0.2s ease",
  },
};
