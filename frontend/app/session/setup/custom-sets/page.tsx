"use client";

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense } from "react";
import ThemeToggle from "../../../components/ThemeToggle";
import { DiceSetPreviewDynamic } from "../../../components/DiceFaceRenderer";

// ── Types ──────────────────────────────────────
type CustomSet = {
  id: string;
  name: string;
  leftTop: number;
  leftFront: number;
  rightTop: number;
  rightFront: number;
  sevenWays: number;
  sevenPct: string;
};

// ── Seven ways calculator ──────────────────────
// Given a starting orientation, calculates how many
// of the 16 on-axis combinations produce a 7
const OPPOSITE: Record<number, number> = { 1:6, 2:5, 3:4, 4:3, 5:2, 6:1 };

function calcSevenWays(lt: number, lf: number, rt: number, rf: number): number {
  const leftFaces = [lt, lf, OPPOSITE[lt], OPPOSITE[lf]];
  const rightFaces = [rt, rf, OPPOSITE[rt], OPPOSITE[rf]];
  let count = 0;
  for (const l of leftFaces) {
    for (const r of rightFaces) {
      if (l + r === 7) count++;
    }
  }
  return count;
}

// Given a selected face, return which faces are invalid for the paired position
// Invalid = the face itself + its opposite (sum to 7)
function getDisabledFaces(selected: number | null): number[] {
  if (!selected) return [];
  return [selected, 7 - selected];
}

// ── Face picker component ──────────────────────
function FacePicker({ label, value, onChange, disabled = [] }: {
  label: string;
  value: number | null;
  onChange: (v: number) => void;
  disabled?: number[];
}) {
  return (
    <div style={styles.pickerWrap}>
      <span style={styles.pickerLabel}>{label}</span>
      <div style={styles.pickerRow}>
        {[1,2,3,4,5,6].map(n => {
          const isDisabled = disabled.includes(n);
          return (
          <button
            key={n}
            style={{
              ...styles.faceBtn,
              ...(value === n ? styles.faceBtnActive : {}),
              ...(isDisabled ? styles.faceBtnDisabled : {}),
            }}
            onClick={() => !isDisabled && onChange(n)}
            disabled={isDisabled}
          >
            {n}
          </button>
          );
        })}
      </div>
    </div>
  );
}

// ── Main page ──────────────────────────────────
function CustomSetsContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const mode = searchParams.get("mode") || "roll";

  const [sets, setSets] = useState<CustomSet[]>([]);
  const [mounted, setMounted] = useState(false);
  const [creating, setCreating] = useState(false);
  const [name, setName] = useState("");
  const [leftTop, setLeftTop] = useState<number | null>(null);
  const [leftFront, setLeftFront] = useState<number | null>(null);
  const [rightTop, setRightTop] = useState<number | null>(null);
  const [rightFront, setRightFront] = useState<number | null>(null);

  // Clear paired face if the new selection makes it invalid
  const handleLeftTop = (v: number) => {
    setLeftTop(v);
    if (leftFront && (leftFront === v || leftFront === 7 - v)) setLeftFront(null);
  };
  const handleLeftFront = (v: number) => {
    setLeftFront(v);
    if (leftTop && (leftTop === v || leftTop === 7 - v)) setLeftTop(null);
  };
  const handleRightTop = (v: number) => {
    setRightTop(v);
    if (rightFront && (rightFront === v || rightFront === 7 - v)) setRightFront(null);
  };
  const handleRightFront = (v: number) => {
    setRightFront(v);
    if (rightTop && (rightTop === v || rightTop === 7 - v)) setRightTop(null);
  };

  // Load saved sets from local storage
  useEffect(() => {
    setMounted(true);
    try {
      const saved = localStorage.getItem("diceiq-custom-sets");
      if (saved) setSets(JSON.parse(saved));
    } catch {}
  }, []);

  const saveToStorage = (updated: CustomSet[]) => {
    localStorage.setItem("diceiq-custom-sets", JSON.stringify(updated));
    setSets(updated);
  };

  // Top and front can't be opposite faces (sum to 7)
  const isValidPair = (top: number | null, front: number | null) =>
    top && front ? top + front !== 7 : true;
  const leftValid = isValidPair(leftTop, leftFront);
  const rightValid = isValidPair(rightTop, rightFront);
  const canSave = name.trim() && leftTop && leftFront && rightTop && rightFront && leftValid && rightValid;

  const handleSave = () => {
    if (!canSave) return;
    const ways = calcSevenWays(leftTop!, leftFront!, rightTop!, rightFront!);
    const pct = Math.round((ways / 16) * 100) + "%";
    const newSet: CustomSet = {
      id: Date.now().toString(),
      name: name.trim(),
      leftTop: leftTop!,
      leftFront: leftFront!,
      rightTop: rightTop!,
      rightFront: rightFront!,
      sevenWays: ways,
      sevenPct: pct,
    };
    saveToStorage([...sets, newSet]);
    setCreating(false);
    setName(""); setLeftTop(null); setLeftFront(null);
    setRightTop(null); setRightFront(null);
  };

  const handleDelete = (id: string) => {
    saveToStorage(sets.filter(s => s.id !== id));
  };

  const handleSelect = (set: CustomSet) => {
    router.push(`/session/setup/confirm?mode=${mode}&set=custom-${set.id}&setName=${encodeURIComponent(set.name)}&sevenWays=${set.sevenWays}&sevenPct=${set.sevenPct}`);
  };

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
        <span style={styles.stepLabel}>CUSTOM SETS</span>
        <ThemeToggle />
      </div>

      {/* ── Header ── */}
      <div style={styles.header}>
        <h2 style={styles.title}>My Dice Sets</h2>
        <p style={styles.subtitle}>Your saved custom sets</p>
      </div>

      {/* ── Create Form ── */}
      {creating && (
        <div style={styles.form}>
          <input
            style={styles.nameInput}
            placeholder="Set name (e.g. My Power Set)"
            value={name}
            onChange={e => setName(e.target.value)}
            maxLength={30}
          />
          <div style={styles.diceRow}>
            <div style={styles.dieSection}>
              <span style={styles.dieSectionLabel}>LEFT DIE</span>
              <FacePicker label="Top" value={leftTop} onChange={handleLeftTop} disabled={getDisabledFaces(leftFront)} />
              <FacePicker label="Front" value={leftFront} onChange={handleLeftFront} disabled={getDisabledFaces(leftTop)} />
            </div>
            <div style={styles.dieDivider} />
            <div style={styles.dieSection}>
              <span style={styles.dieSectionLabel}>RIGHT DIE</span>
              <FacePicker label="Top" value={rightTop} onChange={handleRightTop} disabled={getDisabledFaces(rightFront)} />
              <FacePicker label="Front" value={rightFront} onChange={handleRightFront} disabled={getDisabledFaces(rightTop)} />
            </div>
          </div>
          {leftTop && leftFront && rightTop && rightFront && (
            <div style={{
              display: "flex", flexDirection: "column" as const, gap: 8,
              padding: "10px 12px",
              background: "var(--bg-raised)",
              borderRadius: "8px",
              border: "1px solid var(--border)",
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={styles.previewLabel}>Dice Preview</span>
                <DiceSetPreviewDynamic
                  leftTop={leftTop} leftFront={leftFront}
                  rightTop={rightTop} rightFront={rightFront}
                />
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={styles.previewLabel}>7s</span>
                <span style={{
                  ...styles.previewValue,
                  color: calcSevenWays(leftTop,leftFront,rightTop,rightFront) <= 2
                    ? "#2ECC71" : "#F39C12"
                }}>
                  {calcSevenWays(leftTop,leftFront,rightTop,rightFront)} ways ·{" "}
                  {Math.round((calcSevenWays(leftTop,leftFront,rightTop,rightFront)/16)*100)}%
                </span>
              </div>
            </div>
          )}
          <div style={styles.formBtns}>
            <button className="btn-ghost" style={styles.cancelBtn}
              onClick={() => setCreating(false)}>Cancel</button>
            <button className="btn-primary" style={{
              ...styles.saveBtn,
              opacity: canSave ? 1 : 0.4,
              cursor: canSave ? "pointer" : "not-allowed",
            }}
              disabled={!canSave}
              onClick={handleSave}>Save Set</button>
          </div>
        </div>
      )}

      {/* ── Sets Grid ── */}
      {!creating && mounted && (
        <div style={styles.grid}>
          {sets.map(set => (
            <div key={set.id} style={styles.card} onClick={() => handleSelect(set)}>
              <span style={{ ...styles.phaseBadge, color: "#B8C4D0", borderColor: "#B8C4D0" }}>
                Custom
              </span>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", width: "100%", gap: 4 }}>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <h3 style={styles.setName}>{set.name}</h3>
                  <p style={styles.setTarget}>
                    L: {set.leftTop}t/{set.leftFront}f — R: {set.rightTop}t/{set.rightFront}f
                  </p>
                </div>
                <DiceSetPreviewDynamic
                  leftTop={set.leftTop} leftFront={set.leftFront}
                  rightTop={set.rightTop} rightFront={set.rightFront}
                />
              </div>
              <div style={styles.setMeta}>
                <span style={styles.metaLabel}>7s</span>
                <span style={{ ...styles.metaValue, color: set.sevenWays <= 2 ? "#2ECC71" : "#F39C12" }}>
                  {set.sevenWays} ways · {set.sevenPct}
                </span>
              </div>
              <button style={styles.deleteBtn}
                onClick={e => { e.stopPropagation(); handleDelete(set.id); }}>
                ✕
              </button>
            </div>
          ))}

          {/* Create New Card */}
          <button style={styles.createCard} onClick={() => setCreating(true)}>
            <div style={styles.createIcon}>＋</div>
            <h3 style={styles.createName}>Create New Set</h3>
            <p style={styles.createDesc}>Define your own orientation</p>
          </button>
        </div>
      )}

      {/* ── Empty State ── */}
      {!creating && mounted && sets.length === 0 && (
        <div style={styles.emptyState}>
          <p style={styles.emptyText}>No custom sets yet.</p>
          <p style={styles.emptySubtext}>Tap Create New Set to get started.</p>
        </div>
      )}

    </main>
  );
}

export default function CustomSetsPage() {
  return (
    <Suspense>
      <CustomSetsContent />
    </Suspense>
  );
}

const styles: Record<string, React.CSSProperties> = {
  page: {
    minHeight: "100dvh",
    display: "flex",
    flexDirection: "column",
    padding: "12px 16px 24px",
    background: "var(--bg-primary)",
    maxWidth: "420px",
    margin: "0 auto",
    width: "100%",
    gap: "14px",
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
  form: {
    background: "var(--bg-surface)",
    border: "1px solid var(--border)",
    borderRadius: "14px",
    padding: "16px",
    display: "flex", flexDirection: "column", gap: "14px",
  },
  nameInput: {
    background: "var(--bg-raised)",
    border: "1px solid var(--border)",
    borderRadius: "8px",
    padding: "12px 14px",
    color: "var(--text-primary)",
    fontFamily: "var(--font-body)",
    fontSize: "0.9rem",
    outline: "none",
    width: "100%",
  },
  diceRow: {
    display: "flex", gap: "12px", alignItems: "flex-start",
  },
  dieSection: {
    flex: 1, display: "flex", flexDirection: "column", gap: "8px",
  },
  dieSectionLabel: {
    fontSize: "0.6rem", color: "var(--silver-mid)",
    letterSpacing: "0.12em", fontFamily: "var(--font-mono)",
    textTransform: "uppercase" as const,
  },
  dieDivider: {
    width: "1px", background: "var(--border)", alignSelf: "stretch",
  },
  pickerWrap: { display: "flex", flexDirection: "column", gap: "5px" },
  pickerLabel: {
    fontSize: "0.6rem", color: "var(--text-muted)",
    fontFamily: "var(--font-mono)", letterSpacing: "0.08em",
  },
  pickerRow: { display: "flex", gap: "4px" },
  faceBtn: {
    flex: 1, padding: "12px 0",
    background: "var(--bg-raised)",
    border: "1px solid var(--border)",
    borderRadius: "8px",
    color: "var(--text-secondary)",
    fontFamily: "var(--font-mono)",
    fontSize: "1rem", fontWeight: 600,
    cursor: "pointer",
    transition: "all 0.15s ease",
    minHeight: "44px",
  },
  faceBtnActive: {
    background: "var(--blue-electric)",
    border: "1px solid var(--blue-electric)",
    color: "white",
  },
  faceBtnDisabled: {
    opacity: 0.2,
    cursor: "not-allowed",
  },
  preview: {
    display: "flex", justifyContent: "space-between", alignItems: "center",
    padding: "8px 12px",
    background: "var(--bg-raised)",
    borderRadius: "8px",
    border: "1px solid var(--border)",
  },
  previewLabel: {
    fontSize: "0.7rem", color: "var(--text-muted)",
    fontFamily: "var(--font-mono)", letterSpacing: "0.08em",
  },
  previewValue: {
    fontSize: "0.85rem", fontWeight: 600, fontFamily: "var(--font-mono)",
  },
  formBtns: { display: "flex", gap: "10px" },
  cancelBtn: { flex: 1, padding: "12px", fontSize: "0.85rem" },
  saveBtn: { flex: 1, padding: "12px", fontSize: "0.85rem", borderRadius: "8px" },
  grid: {
    display: "grid", gridTemplateColumns: "1fr 1fr",
    gap: "10px",
    alignItems: "start",
  },
  card: {
    display: "flex", flexDirection: "column", alignItems: "flex-start",
    gap: "4px", padding: "10px",
    background: "var(--bg-surface)",
    border: "1px solid var(--border)",
    borderRadius: "10px",
    cursor: "pointer", textAlign: "left",
    transition: "all 0.2s ease",
    position: "relative", width: "100%",
  },
  phaseBadge: {
    fontSize: "0.55rem", letterSpacing: "0.08em",
    textTransform: "uppercase" as const,
    fontFamily: "var(--font-mono)",
    border: "1px solid", borderRadius: "4px", padding: "1px 5px",
  },
  setName: {
    fontSize: "0.9rem", fontFamily: "var(--font-display)",
    fontWeight: 600, color: "var(--text-primary)", lineHeight: 1.2,
  },
  setTarget: { fontSize: "0.7rem", color: "var(--text-muted)", lineHeight: 1.3 },
  setMeta: { display: "flex", flexDirection: "column" as const, gap: "1px", marginTop: "2px" },
  metaLabel: {
    fontSize: "0.55rem", color: "var(--text-muted)",
    letterSpacing: "0.08em", textTransform: "uppercase" as const,
    fontFamily: "var(--font-mono)",
  },
  metaValue: { fontSize: "0.75rem", fontWeight: 600, fontFamily: "var(--font-mono)" },
  deleteBtn: {
    position: "absolute" as const, top: "8px", right: "8px",
    background: "transparent", border: "none",
    color: "var(--text-muted)", fontSize: "0.65rem",
    cursor: "pointer", padding: "2px 4px",
    lineHeight: 1,
  },
  createCard: {
    display: "flex", flexDirection: "column" as const,
    alignItems: "center", justifyContent: "center",
    gap: "6px", padding: "10px",
    background: "transparent",
    border: "1px dashed var(--border-bright)",
    borderRadius: "10px",
    cursor: "pointer", width: "100%",
    transition: "all 0.2s ease",
  },
  createIcon: { fontSize: "1.3rem", color: "var(--silver-mid)" },
  createName: {
    fontSize: "0.85rem", fontFamily: "var(--font-display)",
    fontWeight: 600, color: "var(--silver-mid)",
  },
  createDesc: { fontSize: "0.62rem", color: "var(--text-muted)", textAlign: "center" as const },
  emptyState: {
    flex: 1, display: "flex", flexDirection: "column",
    alignItems: "center", justifyContent: "center", gap: "6px",
  },
  emptyText: { color: "var(--text-secondary)", fontSize: "0.9rem" },
  emptySubtext: { color: "var(--text-muted)", fontSize: "0.75rem" },
  errorText: {
    fontSize: "0.6rem", color: "#E74C3C",
    fontFamily: "var(--font-mono)", letterSpacing: "0.03em",
  },
};
