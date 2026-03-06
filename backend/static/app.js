// DiceIQ — Frontend App Logic
// Voice recognition, game state, API calls, haptics
// Runs entirely in Safari on iPhone — no install needed

// ─────────────────────────────────────────────────────────────
// GAME STATE
// Everything the app knows about the current session
// ─────────────────────────────────────────────────────────────

const state = {
  sessionId:    null,
  handId:       null,
  handNumber:   1,
  phase:        'come_out',
  currentPoint: null,
  rollCount:    0,
  isActive:     false,
  isListening:  false,
};

// ─────────────────────────────────────────────────────────────
// API — talks to Flask backend
// ─────────────────────────────────────────────────────────────

const API = {
  // Auto-detect — same machine serving the page
  base: window.location.origin + '/api',

  async ping() {
    try {
      const r = await fetch(`${this.base}/ping`);
      return r.ok;
    } catch { return false; }
  },

  async startSession(diceSet, location) {
    const r = await fetch(`${this.base}/session/start`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ dice_set: diceSet, location })
    });
    return r.json();
  },

  async processVoice(text) {
    const r = await fetch(`${this.base}/session/${state.sessionId}/voice`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({
        text,
        hand_id:       state.handId,
        phase:         state.phase,
        current_point: state.currentPoint,
      })
    });
    return r.json();
  },

  async endSession() {
    const r = await fetch(`${this.base}/session/${state.sessionId}/end`, {
      method: 'POST'
    });
    return r.json();
  },

  async getAnalytics() {
    const r = await fetch(`${this.base}/session/${state.sessionId}/analytics`);
    return r.json();
  }
};

// ─────────────────────────────────────────────────────────────
// SPEECH RECOGNITION
// Uses Web Speech API — works in Safari on iOS
// ─────────────────────────────────────────────────────────────

let recognition = null;

function initSpeech() {
  const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    showAlert('Voice not supported in this browser', 'alert');
    return false;
  }

  recognition = new SpeechRecognition();
  recognition.lang        = 'en-US';
  recognition.continuous  = false;
  recognition.interimResults = false;
  recognition.maxAlternatives = 3;

  recognition.onresult = async (event) => {
    const text = event.results[0][0].transcript.toLowerCase().trim();
    updateHeardText(text);
    await handleVoiceInput(text);
  };

  recognition.onerror = (event) => {
    console.error('Speech error:', event.error);
    setMicState('idle');
    // Auto-restart if session still active
    if (state.isActive && state.isListening) {
      setTimeout(() => startListening(), 500);
    }
  };

  recognition.onend = () => {
    // Keep listening if session is active
    if (state.isActive && state.isListening) {
      setTimeout(() => recognition.start(), 300);
    } else {
      setMicState('idle');
    }
  };

  return true;
}

function toggleListening() {
  if (!state.isActive) return;

  if (state.isListening) {
    stopListening();
  } else {
    startListening();
  }
}

function startListening() {
  if (!recognition) return;
  try {
    recognition.start();
    state.isListening = true;
    setMicState('listening');
  } catch (e) {
    // Already started — ignore
  }
}

function stopListening() {
  if (!recognition) return;
  state.isListening = false;
  recognition.stop();
  setMicState('idle');
}

// ─────────────────────────────────────────────────────────────
// VOICE HANDLER
// Sends to Flask, updates UI, fires haptics + audio
// ─────────────────────────────────────────────────────────────

async function handleVoiceInput(text) {
  try {
    const response = await API.processVoice(text);

    if (response.status === 'ok') {
      // Update game state
      updateStateFromResponse(response);

      // Update UI
      updatePlayScreen(response);

      // Haptics
      triggerHaptic(response.haptic);

      // Audio confirmation to hearing aids
      if (response.audio) {
        speak(response.audio);
      }

      // Diagnostic alert — slight delay so it doesn't overlap
      if (response.alert) {
        setTimeout(() => {
          showAlert(response.alert.message, response.alert.level);
          speak(response.alert.message);
        }, 1200);
      } else {
        hideAlert();
      }

    } else {
      // Couldn't understand
      triggerHaptic('double');
      speak('Repeat that');
      updateHeardText('? ' + text);
    }

  } catch (err) {
    speak('Connection lost');
    showAlert('Connection lost — check WiFi', 'alert');
  }
}

// ─────────────────────────────────────────────────────────────
// STATE UPDATES
// ─────────────────────────────────────────────────────────────

function updateStateFromResponse(r) {
  if (r.phase)       state.phase        = r.phase;
  if (r.new_point !== undefined) state.currentPoint = r.new_point;
  if (r.new_hand_id) state.handId       = r.new_hand_id;
  if (r.type === 'roll') state.rollCount++;
  if (r.hand_number) state.handNumber   = r.hand_number;
}

// ─────────────────────────────────────────────────────────────
// UI UPDATES
// ─────────────────────────────────────────────────────────────

function updatePlayScreen(r) {
  // Phase display
  const phaseEl = document.getElementById('phase-display');
  if (state.phase === 'come_out') {
    phaseEl.textContent = 'COME OUT';
    phaseEl.className   = 'phase-display come-out';
  } else {
    phaseEl.textContent = `POINT  ${state.currentPoint}`;
    phaseEl.className   = 'phase-display point';
  }

  // Dice display
  if (r.type === 'roll') {
    document.getElementById('left-die').textContent    = r.left;
    document.getElementById('right-die').textContent   = r.right;
    document.getElementById('total-display').textContent = r.total;
    document.getElementById('result-label').textContent =
      formatResultType(r.result_type);
  }

  // Stats
  document.getElementById('roll-count').textContent = state.rollCount;
  document.getElementById('hand-count').textContent = state.handNumber;

  // SRR — update from response if available
  if (r.srr) {
    document.getElementById('srr-display').textContent = r.srr;
  }
}

function formatResultType(type) {
  const labels = {
    'natural':    '★ WINNER',
    'craps':      'CRAPS',
    'point_set':  'POINT SET',
    'point_made': '★ POINT MADE',
    'seven_out':  '✕ SEVEN OUT',
    'number':     'NUMBER',
  };
  return labels[type] || type.toUpperCase();
}

function setMicState(state) {
  const btn   = document.getElementById('mic-btn');
  const label = document.getElementById('mic-label');
  btn.className = 'mic-btn ' + (state === 'listening' ? 'listening' : '');
  label.textContent = state === 'listening' ? 'LISTENING...' : 'TAP TO LISTEN';
}

function updateHeardText(text) {
  document.getElementById('heard-text').textContent = '"' + text + '"';
}

function showAlert(message, level = 'warning') {
  const el = document.getElementById('alert-banner');
  el.textContent = message.toUpperCase();
  el.className   = `alert-banner ${level}`;
}

function hideAlert() {
  const el = document.getElementById('alert-banner');
  el.className = 'alert-banner hidden';
}

function showScreen(name) {
  document.querySelectorAll('.screen').forEach(s => {
    s.classList.remove('active');
  });
  document.getElementById(`${name}-screen`).classList.add('active');
}

// ─────────────────────────────────────────────────────────────
// HAPTICS
// Vibrates iPhone — felt even when phone is in drink holder
// ─────────────────────────────────────────────────────────────

function triggerHaptic(type) {
  if (!navigator.vibrate) return;
  const patterns = {
    single: [40],
    long:   [200],
    triple: [60, 80, 60, 80, 60],
    double: [80, 60, 80],
  };
  navigator.vibrate(patterns[type] || patterns.single);
}

// ─────────────────────────────────────────────────────────────
// TEXT TO SPEECH
// Speaks through Bluetooth hearing aids
// ─────────────────────────────────────────────────────────────

const synth = window.speechSynthesis;

function speak(text) {
  if (!synth) return;
  synth.cancel(); // Clear queue
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate   = 0.85;  // Slightly slow — clear in casino noise
  utterance.volume = 0.9;
  utterance.pitch  = 1.0;
  synth.speak(utterance);
}

// ─────────────────────────────────────────────────────────────
// SESSION MANAGEMENT
// ─────────────────────────────────────────────────────────────

async function startSession() {
  const diceSet  = document.getElementById('dice-set').value;
  const location = document.getElementById('location').value;

  const response = await API.startSession(diceSet, location);

  if (response.status === 'ok') {
    state.sessionId  = response.session_id;
    state.handId     = response.hand_id;
    state.isActive   = true;
    state.rollCount  = 0;
    state.handNumber = 1;
    state.phase      = 'come_out';

    document.getElementById('session-dice-set').textContent = diceSet;
    showScreen('play');
    initSpeech();
    startListening();
    speak('Session started. Good shooting.');
  }
}

async function endSession() {
  state.isActive   = false;
  state.isListening = false;
  stopListening();

  const response = await API.endSession();
  showResults(response.analytics);
}

function newSession() {
  state.sessionId   = null;
  state.handId      = null;
  state.handNumber  = 1;
  state.phase       = 'come_out';
  state.currentPoint = null;
  state.rollCount   = 0;
  state.isActive    = false;
  showScreen('setup');
}

// ─────────────────────────────────────────────────────────────
// RESULTS SCREEN
// ─────────────────────────────────────────────────────────────

function showResults(analytics) {
  if (!analytics) { showScreen('setup'); return; }

  const srrClass = analytics.srr > 6 ? 'good' : analytics.srr > 5 ? 'warn' : 'bad';
  const axisClass = analytics.axis_pct > 25 ? 'good' : analytics.axis_pct > 16 ? 'warn' : 'bad';

  let html = `
    <div class="result-stat">
      <span class="result-stat-label">TOTAL ROLLS</span>
      <span class="result-stat-value">${analytics.total_rolls}</span>
    </div>
    <div class="result-stat">
      <span class="result-stat-label">TOTAL HANDS</span>
      <span class="result-stat-value">${analytics.total_hands}</span>
    </div>
    <div class="result-stat">
      <span class="result-stat-label">SRR</span>
      <span class="result-stat-value ${srrClass}">1:${analytics.srr || '—'}</span>
    </div>
    <div class="result-stat">
      <span class="result-stat-label">AXIS CONTROL</span>
      <span class="result-stat-value ${axisClass}">${analytics.axis_pct}%</span>
    </div>
    <div class="result-stat">
      <span class="result-stat-label">AVG HAND</span>
      <span class="result-stat-value">${analytics.avg_hand} rolls</span>
    </div>
    <div class="result-stat">
      <span class="result-stat-label">LONGEST HAND</span>
      <span class="result-stat-value good">${analytics.longest_hand} rolls</span>
    </div>
  `;

  if (analytics.signature_nums && analytics.signature_nums.length > 0) {
    html += `<div class="signature-numbers">
      <div class="sig-title">🔥 SIGNATURE NUMBERS</div>`;
    analytics.signature_nums.forEach(s => {
      html += `<div class="sig-number">
        <span>Total ${s.number}</span>
        <span>+${s.deviation}% above expected</span>
      </div>`;
    });
    html += `</div>`;
  }

  document.getElementById('results-content').innerHTML = html;
  showScreen('results');
  speak(`Session complete. ${analytics.total_rolls} rolls. SRR ${analytics.srr}. Axis control ${analytics.axis_pct} percent.`);
}

// ─────────────────────────────────────────────────────────────
// INIT — runs when page loads
// ─────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', async () => {
  // Check connection to Flask
  const statusEl = document.getElementById('connection-status');
  const connected = await API.ping();

  if (connected) {
    statusEl.textContent = '✓ Connected to DiceIQ Brain';
    statusEl.className   = 'status-badge connected';
  } else {
    statusEl.textContent = '✗ Brain offline — start python app.py';
    statusEl.className   = 'status-badge error';
  }

  // Wire up start button
  document.getElementById('start-btn').addEventListener('click', startSession);
});
