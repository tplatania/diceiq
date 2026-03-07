"use client";

import Image from "next/image";
import { useRouter } from "next/navigation";
import ThemeToggle from "./components/ThemeToggle";

export default function HomePage() {
  const router = useRouter();

  return (
    <main style={styles.page}>

      {/* ── Top Bar ── */}
      <div style={styles.topBar}>
        <span style={styles.versionTag}>v1.0</span>
        <ThemeToggle />
      </div>

      {/* ── Hero + Stats Group ── */}
      <div style={styles.heroStatsGroup}>

      {/* ── Hero ── */}
      <div style={styles.hero}>
        <div style={styles.logoWrap}>
          <Image
            src="/diceiq-logo.jpg"
            alt="DiceIQ Logo"
            width={180}
            height={180}
            style={styles.logo}
            priority
          />
          <div style={styles.logoGlow} />
        </div>

        <h1 style={styles.title}>DiceIQ</h1>
        <p style={styles.tagline}>Physics-Based Dice Control Coaching</p>
      </div>

      {/* ── Stats Strip ── */}
      <div style={styles.statsStrip}>
        <div style={styles.statItem}>
          <span style={styles.statValue}>0</span>
          <span style={styles.statLabel}>Sessions</span>
        </div>
        <div style={styles.statDivider} />
        <div style={styles.statItem}>
          <span style={styles.statValue}>0</span>
          <span style={styles.statLabel}>Total Rolls</span>
        </div>
        <div style={styles.statDivider} />
        <div style={styles.statItem}>
          <span style={styles.statValue}>—</span>
          <span style={styles.statLabel}>Axis Rating</span>
        </div>
      </div>

      {/* ── CTA ── */}
      <div style={styles.ctaWrap}>
        <button
          className="btn-primary"
          style={styles.startBtn}
          onClick={() => router.push("/session/setup")}
        >
          START SESSION
        </button>
        <button
          className="btn-ghost"
          style={styles.analyticsBtn}
          onClick={() => router.push("/analytics")}
        >
          View Analytics
        </button>
      </div>

      </div>{/* end heroStatsGroup */}

      {/* ── Footer ── */}
      <p style={styles.footer}>ProCalcs · DiceIQ.net</p>

    </main>
  );
}

const styles: Record<string, React.CSSProperties> = {
  page: {
    minHeight: "100dvh",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "16px 40px 32px",
    background: "var(--bg-primary)",
    position: "relative",
    overflow: "hidden",
    maxWidth: "420px",
    margin: "0 auto",
    width: "100%",
  },
  topBar: {
    width: "100%",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    paddingTop: "8px",
  },
  versionTag: {
    fontSize: "0.7rem",
    color: "var(--text-muted)",
    letterSpacing: "0.1em",
    fontFamily: "var(--font-mono)",
    border: "1px solid var(--border)",
    borderRadius: "4px",
    padding: "2px 8px",
  },
  hero: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: "12px",
    justifyContent: "center",
  },
  heroStatsGroup: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    width: "100%",
    flex: 1,
    gap: "12px",
  },
  logoWrap: {
    position: "relative",
    marginBottom: "8px",
  },
  logo: {
    borderRadius: "20px",
    boxShadow: "0 0 40px rgba(30, 111, 217, 0.5), 0 0 80px rgba(30, 111, 217, 0.2)",
  },
  logoGlow: {
    position: "absolute",
    inset: 0,
    borderRadius: "20px",
    background: "radial-gradient(circle, rgba(30,111,217,0.15) 0%, transparent 70%)",
    pointerEvents: "none",
  },
  title: {
    fontSize: "clamp(2.2rem, 8vw, 3.5rem)",
    fontFamily: "var(--font-display)",
    fontWeight: 700,
    letterSpacing: "0.15em",
    color: "var(--text-primary)",
    textShadow: "0 0 30px rgba(184, 196, 208, 0.4)",
  },
  tagline: {
    fontSize: "0.8rem",
    color: "var(--text-muted)",
    letterSpacing: "0.12em",
    textTransform: "uppercase",
    fontFamily: "var(--font-mono)",
    textAlign: "center",
  },
  statsStrip: {
    display: "flex",
    alignItems: "center",
    gap: "0",
    background: "var(--bg-surface)",
    border: "1px solid var(--border)",
    borderRadius: "12px",
    padding: "16px 0",
    width: "100%",
  },
  statItem: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: "4px",
  },
  statValue: {
    fontFamily: "var(--font-mono)",
    fontSize: "1.5rem",
    fontWeight: 500,
    color: "var(--silver-mid)",
  },
  statLabel: {
    fontSize: "0.65rem",
    color: "var(--text-muted)",
    letterSpacing: "0.08em",
    textTransform: "uppercase",
  },
  statDivider: {
    width: "1px",
    height: "40px",
    background: "var(--border)",
  },
  ctaWrap: {
    display: "flex",
    flexDirection: "column",
    gap: "12px",
    width: "100%",
    alignItems: "stretch",
  },
  startBtn: {
    width: "100%",
    padding: "18px",
    fontSize: "1.1rem",
    letterSpacing: "0.15em",
    borderRadius: "12px",
  },
  analyticsBtn: {
    width: "100%",
    padding: "14px",
    fontSize: "0.9rem",
  },
  footer: {
    fontSize: "0.65rem",
    color: "var(--text-muted)",
    letterSpacing: "0.1em",
    marginTop: "8px",
    fontFamily: "var(--font-mono)",
  },
};
