"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { Suspense } from "react";
import ThemeToggle from "../../../components/ThemeToggle";

const SET_NAMES: Record<string, string> = {
  "all-sevens": "All Sevens",
  "hard-way": "Hard Way",
  "3v-hard-six": "3V Hard Six",
  "parallel-sixes": "Parallel Sixes",
  "crossed-sixes": "Crossed Sixes",
  "mini-v": "Mini-V Hard 4",
  "2v-set": "2V Set",
};

const SET_SEVEN_WAYS: Record<string, { ways: number; pct: string }> = {
  "all-sevens":      { ways: 4, pct: "25%" },
  "hard-way":        { ways: 4, pct: "25%" },
  "3v-hard-six":     { ways: 2, pct: "12%" },
  "parallel-sixes":  { ways: 4, pct: "25%" },
  "crossed-sixes":   { ways: 2, pct: "12%" },
  "mini-v":          { ways: 4, pct: "25%" },
  "2v-set":          { ways: 2, pct: "12%" },
};

const MODE_LABELS: Record<string, { label: string; icon: string; desc: string }> = {
  roll:      { label: "Roll Mode",      icon: "🎯", desc: "Pure mechanics tracking" },
  game:      { label: "Game Mode",      icon: "🎲", desc: "Full craps simulation" },
  challenge: { label: "Challenge Mode", icon: "🏆", desc: "Goal-based practice" },
};

function ConfirmContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const mode = searchParams.get("mode") || "roll";
  const setId = searchParams.get("set") || "";
  const customSetName = searchParams.get("setName") || "";
  const customWays = searchParams.get("sevenWays") || "";
  const customPct = searchParams.get("sevenPct") || "";

  const isCustom = setId.startsWith("custom-");
  const setName = isCustom ? customSetName : (SET_NAMES[setId] || setId);
  const sevenWays = isCustom
    ? { ways: parseInt(customWays), pct: customPct }
    : SET_SEVEN_WAYS[setId] || { ways: 4, pct: "25%" };

  const modeInfo = MODE_LABELS[mode] || MODE_LABELS.roll;

  return (
    <main style={styles.page}>

      {/* ── Top Bar ── */}
      <div style={styles.topBar}>
        <button style={styles.backBtn}
          onClick={() => router.push(`/session/setup/dice-set?mode=${mode}`)}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="15 18 9 12 15 6"/>
          </svg>
        </button>
        <span style={styles.stepLabel}>STEP 3 OF 3</span>
        <ThemeToggle />
      </div>

      {/* ── Header ── */}
      <div style={styles.header}>
        <h2 style={styles.title}>Ready to Throw</h2>
        <p style={styles.subtitle}>Confirm your session settings</p>
      </div>

      {/* ── Summary Card ── */}
      <div style={styles.summaryCard}>

        {/* Mode Row */}
        <div style={styles.summaryRow}>
          <div style={styles.summaryLeft}>
            <span style={styles.summaryIcon}>{modeInfo.icon}</span>
            <div style={styles.summaryText}>
              <span style={styles.summaryLabel}>Mode</span>
              <span style={styles.summaryValue}>{modeInfo.label}</span>
              <span style={styles.summaryDesc}>{modeInfo.desc}</span>
            </div>
          </div>
          <button style={styles.changeBtn}
            onClick={() => router.push("/session/setup")}>
            Change
          </button>
        </div>

        <div style={styles.divider} />

        {/* Dice Set Row */}
        <div style={styles.summaryRow}>
          <div style={styles.summaryLeft}>
            <span style={styles.summaryIcon}>🎲</span>
            <div style={styles.summaryText}>
              <span style={styles.summaryLabel}>Dice Set</span>
              <span style={styles.summaryValue}>{setName}</span>
              <span style={{
                ...styles.summaryDesc,
                color: sevenWays.ways <= 2 ? "#2ECC71" : "#F39C12",
              }}>
                {sevenWays.ways} ways to seven · {sevenWays.pct}
              </span>
            </div>
          </div>
          <button style={styles.changeBtn}
            onClick={() => router.push(`/session/setup/dice-set?mode=${mode}`)}>
            Change
          </button>
        </div>

      </div>
      {/* ── Physics Insight ── */}
      <div style={styles.insightCard}>
        <span style={styles.insightIcon}>⚡</span>
        <p style={styles.insightText}>
          DiceIQ tracks all 4 die faces every throw — left top, left front,
          right top, right front — to compute your true axis control score.
        </p>
      </div>

      {/* ── Spacer ── */}
      <div style={{ flex: 1 }} />

      {/* ── Start Button ── */}
      <button
        className="btn-primary"
        style={styles.startBtn}
        onClick={() => router.push(`/session/active?mode=${mode}&set=${setId}&setName=${encodeURIComponent(setName)}`)}
      >
        START SESSION
      </button>

    </main>
  );
}

export default function ConfirmPage() {
  return (
    <Suspense>
      <ConfirmContent />
    </Suspense>
  );
}

const styles: Record<string, React.CSSProperties> = {
  page: {
    minHeight: "100dvh",
    display: "flex",
    flexDirection: "column",
    padding: "12px 16px 32px",
    background: "var(--bg-primary)",
    maxWidth: "420px",
    margin: "0 auto",
    width: "100%",
    gap: "16px",
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
    width: "36px", height: "36px",
    display: "flex", alignItems: "center", justifyContent: "center",
    cursor: "pointer", color: "var(--text-muted)",
  },
  stepLabel: {
    fontSize: "0.65rem", color: "var(--text-muted)",
    letterSpacing: "0.15em", fontFamily: "var(--font-mono)",
  },
  header: { display: "flex", flexDirection: "column", gap: "4px" },
  title: {
    fontSize: "clamp(1.4rem, 4vw, 1.8rem)",
    fontFamily: "var(--font-display)", fontWeight: 700,
    letterSpacing: "0.08em", color: "var(--text-primary)",
  },
  subtitle: { fontSize: "0.8rem", color: "var(--text-muted)" },
  summaryCard: {
    background: "var(--bg-surface)",
    border: "1px solid var(--border)",
    borderRadius: "14px",
    padding: "4px 0",
    display: "flex",
    flexDirection: "column",
  },
  summaryRow: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "16px 16px",
    gap: "12px",
  },
  summaryLeft: {
    display: "flex",
    alignItems: "flex-start",
    gap: "12px",
    flex: 1,
  },
  summaryIcon: { fontSize: "1.4rem", lineHeight: 1, marginTop: "2px" },
  summaryText: {
    display: "flex", flexDirection: "column", gap: "2px",
  },
  summaryLabel: {
    fontSize: "0.6rem", color: "var(--text-muted)",
    letterSpacing: "0.1em", fontFamily: "var(--font-mono)",
    textTransform: "uppercase" as const,
  },
  summaryValue: {
    fontSize: "1rem", fontFamily: "var(--font-display)",
    fontWeight: 600, color: "var(--text-primary)", letterSpacing: "0.04em",
  },
  summaryDesc: {
    fontSize: "0.72rem", color: "var(--text-secondary)",
  },
  changeBtn: {
    background: "transparent",
    border: "1px solid var(--border)",
    borderRadius: "6px",
    padding: "6px 12px",
    color: "var(--silver-mid)",
    fontSize: "0.72rem",
    fontFamily: "var(--font-body)",
    cursor: "pointer",
    whiteSpace: "nowrap" as const,
    flexShrink: 0,
  },
  divider: {
    height: "1px",
    background: "var(--border)",
    margin: "0 16px",
  },
  insightCard: {
    background: "var(--bg-surface)",
    border: "1px solid var(--border)",
    borderLeft: "3px solid var(--blue-electric)",
    borderRadius: "10px",
    padding: "14px 16px",
    display: "flex",
    gap: "12px",
    alignItems: "flex-start",
  },
  insightIcon: { fontSize: "1rem", lineHeight: 1, marginTop: "2px" },
  insightText: {
    fontSize: "0.78rem",
    color: "var(--text-secondary)",
    lineHeight: 1.5,
  },
  startBtn: {
    width: "100%",
    padding: "18px",
    fontSize: "1rem",
    fontFamily: "var(--font-display)",
    letterSpacing: "0.12em",
    borderRadius: "12px",
    fontWeight: 700,
  },
};
