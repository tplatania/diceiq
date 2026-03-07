"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import ThemeToggle from "../../components/ThemeToggle";

type Mode = "roll" | "game" | "challenge";

const MODES = [
  {
    id: "roll" as Mode,
    icon: "🎯",
    name: "Roll Mode",
    desc: "Pure mechanics practice. Log every throw and track your axis control, rotation signature, and face distribution. No game context.",
  },
  {
    id: "game" as Mode,
    icon: "🎲",
    name: "Game Mode",
    desc: "Full craps simulation. The app tracks come-out rolls, points, and seven-outs automatically. Measures real game performance.",
  },
  {
    id: "challenge" as Mode,
    icon: "🏆",
    name: "Challenge Mode",
    desc: "Set a goal and beat it. Chase personal bests, track your longest hands, and watch your records improve over time.",
  },
];

export default function SessionSetupPage() {
  const router = useRouter();
  const [mode, setMode] = useState<Mode | null>(null);

  return (
    <main style={styles.page}>

      {/* ── Top Bar ── */}
      <div style={styles.topBar}>
        <button style={styles.backBtn} onClick={() => router.push("/")}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="15 18 9 12 15 6"/>
          </svg>
        </button>
        <span style={styles.stepLabel}>STEP 1 OF 3</span>
        <ThemeToggle />
      </div>

      {/* ── Header ── */}
      <div style={styles.header}>
        <h2 style={styles.title}>Select Mode</h2>
        <p style={styles.subtitle}>How are you practicing today?</p>
      </div>

      {/* ── Mode Cards ── */}
      <div style={styles.cardsWrap}>
        {MODES.map((m) => (
          <button
            key={m.id}
            style={{
              ...styles.modeCard,
              ...(mode === m.id ? styles.modeCardActive : {}),
            }}
            onClick={() => setMode(m.id)}
          >
            <div style={styles.modeIcon}>{m.icon}</div>
            <div style={styles.modeContent}>
              <h3 style={styles.modeName}>{m.name}</h3>
              <p style={styles.modeDesc}>{m.desc}</p>
            </div>
            <div style={{
              ...styles.modeCheck,
              ...(mode === m.id ? styles.modeCheckActive : {}),
            }}>
              {mode === m.id && (
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
                  stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
              )}
            </div>
          </button>
        ))}
      </div>

      {/* ── Next Button ── */}
      <div style={styles.footer}>
        <button
          className="btn-primary"
          style={{
            ...styles.nextBtn,
            opacity: mode ? 1 : 0.4,
            cursor: mode ? "pointer" : "not-allowed",
          }}
          disabled={!mode}
          onClick={() => mode && router.push(`/session/setup/dice-set?mode=${mode}`)}
        >
          NEXT — SELECT DICE SET
        </button>
      </div>

    </main>
  );
}

const styles: Record<string, React.CSSProperties> = {
  page: {
    minHeight: "100dvh",
    display: "flex",
    flexDirection: "column",
    padding: "16px 24px 32px",
    background: "var(--bg-primary)",
    maxWidth: "420px",
    margin: "0 auto",
    width: "100%",
    gap: "20px",
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
    gap: "6px",
  },
  title: {
    fontSize: "clamp(1.6rem, 5vw, 2rem)",
    fontFamily: "var(--font-display)",
    fontWeight: 700,
    letterSpacing: "0.08em",
    color: "var(--text-primary)",
  },
  subtitle: {
    fontSize: "0.85rem",
    color: "var(--text-muted)",
    fontFamily: "var(--font-body)",
  },
  cardsWrap: {
    display: "flex",
    flexDirection: "column",
    gap: "12px",
    flex: 1,
    alignItems: "stretch",
  },
  modeCard: {
    display: "flex",
    alignItems: "flex-start",
    gap: "14px",
    padding: "18px",
    background: "var(--bg-surface)",
    border: "1px solid var(--border)",
    borderRadius: "14px",
    cursor: "pointer",
    textAlign: "left",
    transition: "all 0.2s ease",
    width: "100%",
    flex: 1,
  },
  modeCardActive: {
    border: "1px solid var(--blue-electric)",
    background: "rgba(30, 111, 217, 0.08)",
    boxShadow: "0 0 20px rgba(30, 111, 217, 0.15)",
  },
  modeIcon: {
    fontSize: "1.6rem",
    lineHeight: 1,
    flexShrink: 0,
    marginTop: "2px",
  },
  modeContent: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    gap: "5px",
  },
  modeName: {
    fontSize: "1rem",
    fontFamily: "var(--font-display)",
    fontWeight: 600,
    letterSpacing: "0.05em",
    color: "var(--text-primary)",
  },
  modeDesc: {
    fontSize: "0.78rem",
    color: "var(--text-muted)",
    lineHeight: 1.5,
    fontFamily: "var(--font-body)",
  },
  modeCheck: {
    width: "22px",
    height: "22px",
    borderRadius: "50%",
    border: "1px solid var(--border)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    flexShrink: 0,
    marginTop: "2px",
    transition: "all 0.2s ease",
    color: "white",
  },
  modeCheckActive: {
    background: "var(--blue-electric)",
    border: "1px solid var(--blue-electric)",
  },
  footer: {
    paddingTop: "4px",
  },
  nextBtn: {
    width: "100%",
    padding: "18px",
    fontSize: "0.95rem",
    letterSpacing: "0.12em",
    borderRadius: "12px",
    transition: "opacity 0.2s ease",
  },
};
