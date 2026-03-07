"use client";

import { useState, useEffect, useCallback, useRef, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useConversation } from "@elevenlabs/react";

const AGENT_ID = "agent_5601kk34y9fkedcrwp3nzxg7bks3";

// ── Types ─────────────────────────────────────
type RollEntry = {
  id: number;
  rollNumber: number;
  leftTop: number;
  leftFront: number;
  rightTop: number;
  rightFront: number;
  total: number;
  resultType: string;
  timestamp: Date;
};

type GameState = "come_out" | "point" | "seven_out";

// ── Face Picker (reused from custom sets) ─────
function FacePicker({ label, value, onChange }: {
  label: string; value: number | null; onChange: (v: number) => void;
}) {
  return (
    <div style={s.pickerWrap}>
      <span style={s.pickerLabel}>{label}</span>
      <div style={s.pickerRow}>
        {[1,2,3,4,5,6].map(n => (
          <button key={n} style={{ ...s.faceBtn, ...(value === n ? s.faceBtnActive : {}) }}
            onClick={() => onChange(n)}>{n}</button>
        ))}
      </div>
    </div>
  );
}

// ── Voice Orb ─────────────────────────────────
function VoiceOrb({ status, isSpeaking }: { status: string; isSpeaking: boolean }) {
  return (
    <div style={s.orbContainer}>
      <div style={{
        ...s.orbOuter,
        ...(isSpeaking ? s.orbSpeaking : status === "connected" ? s.orbListening : s.orbIdle),
      }}>
        <div style={{ ...s.orbInner, ...(isSpeaking ? s.orbInnerSpeaking : {}) }}>
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none"
            stroke={status === "connected" ? "#1E6FD9" : "#7A8A99"}
            strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
            <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
            <line x1="12" y1="19" x2="12" y2="23"/>
            <line x1="8" y1="23" x2="16" y2="23"/>
          </svg>
        </div>
      </div>
      <span style={s.orbLabel}>
        {isSpeaking ? "Coach is speaking..." :
         status === "connected" ? "Coach is listening..." :
         status === "connecting" ? "Connecting..." : "Coach offline"}
      </span>
    </div>
  );
}

// ── Game State Banner ─────────────────────────
function GameBanner({ mode, gameState, point, challengeGoal, rollCount }:
  { mode: string; gameState: GameState; point: number | null;
    challengeGoal: number; rollCount: number }) {
  if (mode === "roll") return (
    <div style={s.banner}>
      <span style={s.bannerLabel}>ROLL MODE</span>
      <span style={s.bannerValue}>Throw #{rollCount}</span>
    </div>
  );
  if (mode === "challenge") return (
    <div style={s.banner}>
      <span style={s.bannerLabel}>GOAL</span>
      <span style={s.bannerValue}>{rollCount} / {challengeGoal} rolls</span>
      <div style={s.progressBar}>
        <div style={{ ...s.progressFill,
          width: `${Math.min((rollCount / challengeGoal) * 100, 100)}%` }} />
      </div>
    </div>
  );
  // Game mode
  const color = gameState === "come_out" ? "#2ECC71" :
                gameState === "seven_out" ? "#8B1A1A" : "#1E6FD9";
  const label = gameState === "come_out" ? "COME OUT" :
                gameState === "seven_out" ? "SEVEN OUT" :
                `POINT: ${point}`;
  return (
    <div style={{ ...s.banner, borderColor: color }}>
      <span style={{ ...s.bannerGameLabel, color }}>●</span>
      <span style={{ ...s.bannerValue, color }}>{label}</span>
    </div>
  );
}

// ── Main Active Session ───────────────────────
function ActiveSessionContent() {
  const router = useRouter();
  const params = useSearchParams();
  const mode = params.get("mode") || "roll";
  const setName = params.get("setName") || "Hard Way";

  // Timer
  const [elapsed, setElapsed] = useState(0);
  useEffect(() => {
    const t = setInterval(() => setElapsed(e => e + 1), 1000);
    return () => clearInterval(t);
  }, []);
  const formatTime = (s: number) =>
    `${String(Math.floor(s/60)).padStart(2,"0")}:${String(s%60).padStart(2,"0")}`;

  // Session state
  const [rolls, setRolls] = useState<RollEntry[]>([]);
  const [gameState, setGameState] = useState<GameState>("come_out");
  const [point, setPoint] = useState<number | null>(null);
  const rollCounter = useRef(0);

  // Correction sheet
  const [correcting, setCorrecting] = useState<RollEntry | null>(null);
  const [cLT, setCLT] = useState<number|null>(null);
  const [cLF, setCLF] = useState<number|null>(null);
  const [cRT, setCRT] = useState<number|null>(null);
  const [cRF, setCRF] = useState<number|null>(null);
  const [corrected, setCorrected] = useState(false);

  // End session confirm
  const [confirmEnd, setConfirmEnd] = useState(false);

  // ElevenLabs
  const conversation = useConversation({
    onConnect: () => console.log("DiceIQ Coach connected"),
    onDisconnect: () => console.log("DiceIQ Coach disconnected"),
    onError: (e) => console.error("Voice error:", e),
  });

  const startCoach = useCallback(async () => {
    try {
      await navigator.mediaDevices.getUserMedia({ audio: true });
      await conversation.startSession({ agentId: AGENT_ID, connectionType: "webrtc" });
    } catch (e) {
      console.error("Mic or connection error:", e);
    }
  }, [conversation]);

  useEffect(() => { startCoach(); return () => { conversation.endSession(); }; }, []);

  // Derived stats
  const rollCount = rolls.length;
  const sevens = rolls.filter(r => r.total === 7).length;
  const srr = sevens > 0 ? (rollCount / sevens).toFixed(1) : "—";
  const onAxis = rolls.filter(r => r.leftTop === r.rightTop).length;
  const axisPct = rollCount > 0 ? Math.round((onAxis / rollCount) * 100) + "%" : "—";

  // Open correction sheet
  const openCorrection = (roll: RollEntry) => {
    setCorrecting(roll);
    setCLT(roll.leftTop); setCLF(roll.leftFront);
    setCRT(roll.rightTop); setCRF(roll.rightFront);
    setCorrected(false);
  };

  const submitCorrection = () => {
    if (!correcting || !cLT || !cLF || !cRT || !cRF) return;
    const newTotal = cLT + cRT;
    setRolls(prev => prev.map(r => r.id === correcting.id
      ? { ...r, leftTop: cLT, leftFront: cLF, rightTop: cRT, rightFront: cRF, total: newTotal }
      : r));
    setCorrected(true);
    setTimeout(() => { setCorrecting(null); setCorrected(false); }, 1200);
  };

  const handleEndSession = () => {
    conversation.endSession();
    router.push("/");
  };

  return (
    <main style={s.page}>

      {/* ── Top Bar ── */}
      <div style={s.topBar}>
        <button style={s.exitBtn} onClick={() => setConfirmEnd(true)}>✕</button>
        <div style={s.topCenter}>
          <span style={s.topMode}>{mode.toUpperCase()} · {setName}</span>
        </div>
        <span style={s.timer}>{formatTime(elapsed)}</span>
      </div>

      {/* ── Live Stats ── */}
      <div style={s.statsStrip}>
        {[["ROLLS", rollCount.toString()],
          ["SRR", srr.toString()],
          ["AXIS", axisPct]].map(([label, val]) => (
          <div key={label} style={s.statBlock}>
            <span style={s.statLabel}>{label}</span>
            <span style={s.statValue}>{val}</span>
          </div>
        ))}
      </div>

      {/* ── Mode Banner ── */}
      <GameBanner mode={mode} gameState={gameState} point={point}
        challengeGoal={50} rollCount={rollCount} />

      {/* ── Voice Orb ── */}
      <VoiceOrb status={conversation.status} isSpeaking={conversation.isSpeaking} />

      {/* ── Roll History ── */}
      <div style={s.historySection}>
        <span style={s.historyTitle}>ROLL HISTORY</span>
        <div style={s.historyList}>
          {rolls.length === 0 && (
            <div style={s.historyEmpty}>Rolls will appear here as you throw</div>
          )}
          {[...rolls].reverse().slice(0, 8).map(roll => (
            <button key={roll.id} style={s.historyRow} onClick={() => openCorrection(roll)}>
              <span style={s.historyRollNum}>#{roll.rollNumber}</span>
              <span style={s.historyFaces}>
                {roll.leftTop}·{roll.leftFront} — {roll.rightTop}·{roll.rightFront}
              </span>
              <span style={s.historyTotal}>{roll.total}</span>
              <span style={{
                ...s.historyResult,
                color: roll.total === 7 ? "#8B1A1A" :
                       [7,11].includes(roll.total) ? "#2ECC71" : "#B8C4D0"
              }}>{roll.resultType}</span>
              <span style={s.historyEdit}>✎</span>
            </button>
          ))}
        </div>
      </div>

      {/* ── End Session ── */}
      <button style={s.endBtn} onClick={() => setConfirmEnd(true)}>END SESSION</button>

      {/* ── End Confirm Modal ── */}
      {confirmEnd && (
        <div style={s.overlay}>
          <div style={s.modal}>
            <h3 style={s.modalTitle}>End Session?</h3>
            <p style={s.modalDesc}>
              {rollCount} rolls logged. Your stats will be saved.
            </p>
            <div style={s.modalBtns}>
              <button style={s.modalCancel} onClick={() => setConfirmEnd(false)}>
                Keep Going
              </button>
              <button style={s.modalConfirm} onClick={handleEndSession}>
                End Session
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Correction Slide-Up ── */}
      {correcting && (
        <div style={s.sheetOverlay} onClick={() => setCorrecting(null)}>
          <div style={s.sheet} onClick={e => e.stopPropagation()}>
            {corrected ? (
              <div style={s.correctedFlash}>
                <span style={s.correctedCheck}>✓</span>
                <span style={s.correctedText}>Corrected</span>
              </div>
            ) : (
              <>
                <div style={s.sheetHandle} />
                <h3 style={s.sheetTitle}>Correct Roll #{correcting.rollNumber}</h3>
                <div style={s.sheetDice}>
                  <div style={s.sheetDieCol}>
                    <span style={s.sheetDieLabel}>LEFT DIE</span>
                    <FacePicker label="Top" value={cLT} onChange={setCLT} />
                    <FacePicker label="Front" value={cLF} onChange={setCLF} />
                  </div>
                  <div style={s.sheetDivider} />
                  <div style={s.sheetDieCol}>
                    <span style={s.sheetDieLabel}>RIGHT DIE</span>
                    <FacePicker label="Top" value={cRT} onChange={setCRT} />
                    <FacePicker label="Front" value={cRF} onChange={setCRF} />
                  </div>
                </div>
                <button style={{
                  ...s.sheetConfirm,
                  opacity: (cLT && cLF && cRT && cRF) ? 1 : 0.4,
                  cursor: (cLT && cLF && cRT && cRF) ? "pointer" : "not-allowed",
                }} disabled={!(cLT && cLF && cRT && cRF)}
                  onClick={submitCorrection}>
                  Confirm Correction
                </button>
              </>
            )}
          </div>
        </div>
      )}

    </main>
  );
}

export default function ActiveSessionPage() {
  return <Suspense><ActiveSessionContent /></Suspense>;
}

const s: Record<string, React.CSSProperties> = {
  page: { minHeight: "100dvh", display: "flex", flexDirection: "column",
    padding: "12px 16px 24px", background: "var(--bg-primary)",
    maxWidth: "420px", margin: "0 auto", width: "100%", gap: "12px" },
  topBar: { display: "flex", justifyContent: "space-between",
    alignItems: "center", paddingTop: "8px" },
  exitBtn: { background: "transparent", border: "1px solid var(--border)",
    borderRadius: "8px", width: "36px", height: "36px",
    display: "flex", alignItems: "center", justifyContent: "center",
    cursor: "pointer", color: "var(--text-muted)", fontSize: "0.9rem" },
  topCenter: { display: "flex", flexDirection: "column", alignItems: "center" },
  topMode: { fontSize: "0.65rem", color: "var(--text-muted)",
    letterSpacing: "0.12em", fontFamily: "var(--font-mono)" },
  timer: { fontSize: "1rem", fontFamily: "var(--font-mono)",
    fontWeight: 600, color: "var(--text-primary)", letterSpacing: "0.08em" },
  statsStrip: { display: "flex", background: "var(--bg-surface)",
    border: "1px solid var(--border)", borderRadius: "12px", overflow: "hidden" },
  statBlock: { flex: 1, display: "flex", flexDirection: "column",
    alignItems: "center", padding: "12px 8px", gap: "3px",
    borderRight: "1px solid var(--border)" },
  statLabel: { fontSize: "0.55rem", color: "var(--text-muted)",
    letterSpacing: "0.12em", fontFamily: "var(--font-mono)" },
  statValue: { fontSize: "1.1rem", fontWeight: 700,
    fontFamily: "var(--font-mono)", color: "var(--text-primary)" },
  banner: { display: "flex", alignItems: "center", gap: "10px",
    padding: "10px 14px", background: "var(--bg-surface)",
    border: "1px solid var(--border)", borderRadius: "10px" },
  bannerLabel: { fontSize: "0.6rem", color: "var(--text-muted)",
    letterSpacing: "0.12em", fontFamily: "var(--font-mono)" },
  bannerValue: { fontSize: "0.95rem", fontWeight: 600,
    fontFamily: "var(--font-display)", color: "var(--text-primary)" },
  bannerGameLabel: { fontSize: "0.7rem" },
  progressBar: { flex: 1, height: "4px", background: "var(--bg-raised)",
    borderRadius: "2px", overflow: "hidden" },
  progressFill: { height: "100%", background: "var(--blue-electric)",
    borderRadius: "2px", transition: "width 0.3s ease" },
};

// Orb styles injected via style tag for keyframe animations
if (typeof document !== "undefined") {
  const styleId = "diceiq-orb-styles";
  if (!document.getElementById(styleId)) {
    const el = document.createElement("style");
    el.id = styleId;
    el.textContent = `
      @keyframes orbPulse {
        0%, 100% { box-shadow: 0 0 0 0 rgba(30,111,217,0.4); transform: scale(1); }
        50% { box-shadow: 0 0 0 20px rgba(30,111,217,0); transform: scale(1.03); }
      }
      @keyframes orbSpeak {
        0%, 100% { box-shadow: 0 0 0 0 rgba(30,111,217,0.6); transform: scale(1); }
        25% { box-shadow: 0 0 0 12px rgba(30,111,217,0.2); transform: scale(1.06); }
        75% { box-shadow: 0 0 0 24px rgba(30,111,217,0); transform: scale(1.02); }
      }
    `;
    document.head.appendChild(el);
  }
}

Object.assign(s, {
  orbContainer: { display: "flex", flexDirection: "column",
    alignItems: "center", gap: "12px", padding: "8px 0" },
  orbOuter: { width: "100px", height: "100px", borderRadius: "50%",
    display: "flex", alignItems: "center", justifyContent: "center",
    transition: "all 0.3s ease" },
  orbListening: { background: "rgba(30,111,217,0.1)",
    border: "2px solid rgba(30,111,217,0.4)",
    animation: "orbPulse 2.5s ease-in-out infinite" },
  orbSpeaking: { background: "rgba(30,111,217,0.2)",
    border: "2px solid rgba(30,111,217,0.8)",
    animation: "orbSpeak 0.8s ease-in-out infinite" },
  orbIdle: { background: "var(--bg-surface)",
    border: "2px solid var(--border)" },
  orbInner: { width: "64px", height: "64px", borderRadius: "50%",
    background: "var(--bg-surface)", display: "flex",
    alignItems: "center", justifyContent: "center",
    border: "1px solid var(--border)" },
  orbInnerSpeaking: { background: "rgba(30,111,217,0.15)" },
  orbLabel: { fontSize: "0.72rem", color: "var(--text-muted)",
    letterSpacing: "0.06em", fontFamily: "var(--font-mono)" },
  historySection: { display: "flex", flexDirection: "column", gap: "6px", flex: 1 },
  historyTitle: { fontSize: "0.55rem", color: "var(--text-muted)",
    letterSpacing: "0.12em", fontFamily: "var(--font-mono)" },
  historyList: { display: "flex", flexDirection: "column", gap: "4px" },
  historyEmpty: { fontSize: "0.75rem", color: "var(--text-muted)",
    textAlign: "center", padding: "16px 0" },
  historyRow: { display: "flex", alignItems: "center", gap: "8px",
    padding: "8px 12px", background: "var(--bg-surface)",
    border: "1px solid var(--border)", borderRadius: "8px",
    cursor: "pointer", width: "100%", textAlign: "left" as const },
  historyRollNum: { fontSize: "0.65rem", color: "var(--text-muted)",
    fontFamily: "var(--font-mono)", minWidth: "28px" },
  historyFaces: { fontSize: "0.75rem", color: "var(--text-secondary)",
    fontFamily: "var(--font-mono)", flex: 1 },
  historyTotal: { fontSize: "0.9rem", fontWeight: 700,
    fontFamily: "var(--font-mono)", color: "var(--text-primary)", minWidth: "20px" },
  historyResult: { fontSize: "0.65rem", letterSpacing: "0.06em",
    fontFamily: "var(--font-mono)", minWidth: "70px", textAlign: "right" as const },
  historyEdit: { fontSize: "0.7rem", color: "var(--text-muted)", paddingLeft: "4px" },
  endBtn: { background: "transparent", border: "1px solid var(--border)",
    borderRadius: "10px", padding: "14px", width: "100%",
    color: "var(--text-muted)", fontSize: "0.8rem", letterSpacing: "0.12em",
    fontFamily: "var(--font-display)", cursor: "pointer" },
});

Object.assign(s, {
  overlay: { position: "fixed" as const, inset: 0,
    background: "rgba(0,0,0,0.7)", display: "flex",
    alignItems: "center", justifyContent: "center",
    zIndex: 100, padding: "24px" },
  modal: { background: "var(--bg-surface)", border: "1px solid var(--border)",
    borderRadius: "16px", padding: "24px", width: "100%", maxWidth: "340px" },
  modalTitle: { fontSize: "1.2rem", fontFamily: "var(--font-display)",
    fontWeight: 700, color: "var(--text-primary)", marginBottom: "8px" },
  modalDesc: { fontSize: "0.85rem", color: "var(--text-secondary)",
    marginBottom: "20px" },
  modalBtns: { display: "flex", gap: "10px" },
  modalCancel: { flex: 1, padding: "12px",
    background: "transparent", border: "1px solid var(--border)",
    borderRadius: "8px", color: "var(--text-secondary)",
    fontSize: "0.85rem", cursor: "pointer" },
  modalConfirm: { flex: 1, padding: "12px",
    background: "var(--crimson)", border: "none",
    borderRadius: "8px", color: "white",
    fontSize: "0.85rem", fontWeight: 600, cursor: "pointer" },
  sheetOverlay: { position: "fixed" as const, inset: 0,
    background: "rgba(0,0,0,0.6)", zIndex: 100,
    display: "flex", alignItems: "flex-end" },
  sheet: { background: "var(--bg-surface)",
    borderTop: "1px solid var(--border)",
    borderRadius: "16px 16px 0 0",
    padding: "16px 16px 32px", width: "100%",
    display: "flex", flexDirection: "column", gap: "14px" },
  sheetHandle: { width: "40px", height: "4px",
    background: "var(--border)", borderRadius: "2px",
    margin: "0 auto" },
  sheetTitle: { fontSize: "1rem", fontFamily: "var(--font-display)",
    fontWeight: 600, color: "var(--text-primary)", textAlign: "center" as const },
  sheetDice: { display: "flex", gap: "12px" },
  sheetDieCol: { flex: 1, display: "flex", flexDirection: "column", gap: "8px" },
  sheetDieLabel: { fontSize: "0.6rem", color: "var(--silver-mid)",
    letterSpacing: "0.12em", fontFamily: "var(--font-mono)" },
  sheetDivider: { width: "1px", background: "var(--border)" },
  sheetConfirm: { width: "100%", padding: "14px",
    background: "var(--blue-electric)", border: "none",
    borderRadius: "10px", color: "white", fontSize: "0.9rem",
    fontFamily: "var(--font-display)", fontWeight: 600, letterSpacing: "0.06em" },
  correctedFlash: { display: "flex", flexDirection: "column",
    alignItems: "center", justifyContent: "center",
    gap: "8px", padding: "32px 0" },
  correctedCheck: { fontSize: "2.5rem", color: "#2ECC71" },
  correctedText: { fontSize: "1rem", fontFamily: "var(--font-display)",
    fontWeight: 600, color: "#2ECC71", letterSpacing: "0.08em" },
  pickerWrap: { display: "flex", flexDirection: "column", gap: "5px" },
  pickerLabel: { fontSize: "0.6rem", color: "var(--text-muted)",
    fontFamily: "var(--font-mono)", letterSpacing: "0.08em" },
  pickerRow: { display: "flex", gap: "3px" },
  faceBtn: { flex: 1, padding: "10px 0", minHeight: "40px",
    background: "var(--bg-raised)", border: "1px solid var(--border)",
    borderRadius: "6px", color: "var(--text-secondary)",
    fontFamily: "var(--font-mono)", fontSize: "0.9rem",
    fontWeight: 500, cursor: "pointer" },
  faceBtnActive: { background: "var(--blue-electric)",
    border: "1px solid var(--blue-electric)", color: "white" },
});
