# DiceIQ — Tom's Personal Dice Control Performance Engine

## What This Is
DiceIQ is a hands-free, voice-controlled craps session tracker built for
live casino play. No paper. No looking down. No distraction.

You shoot the dice. You whisper two digits. The app does everything else.

---

## The Setup
- **Phone**: iPhone in the drink holder under the rail, screen up
- **Input**: Voice whisper picked up by iPhone mic (~2 feet)
- **Confirmation**: Audio feedback through Bluetooth hearing aids
- **Haptic**: Apple Watch vibrates to confirm each roll
- **Review**: Full session analytics after play

---

## The Voice Grammar
Every roll is logged with two spoken phrases:

| You Say | What It Means |
|---|---|
| "come out" | Start of a new come-out phase |
| "three two" | Left die: 3, Right die: 2, Total: 5 |
| "point eight" | Point is established at 8 |
| "seven out" | Hand is over — seven out |

**Left die is ALWAYS the first digit. No exceptions.**

The app tracks game state automatically. It knows if you're on a
come-out or in a point phase — you never have to tell it twice.

---

## The Architecture

```
D:\diceiq\
├── backend\        ← Flask API (Python) — The Brain
│   ├── app.py          Main application entry point
│   ├── models.py       Database models (Session, Roll)
│   ├── routes.py       All API endpoints
│   ├── engine.py       SRR, axis, diagnostics logic
│   └── database\       SQLite file lives here
├── frontend\       ← Flutter App (Dart) — The Interface
│   ├── lib\
│   │   ├── main.dart         App entry point
│   │   ├── voice.dart        Speech recognition engine
│   │   ├── haptics.dart      Watch + phone vibration
│   │   ├── api.dart          Talks to Flask backend
│   │   └── dashboard.dart    Post-session analytics screen
└── docs\           ← Architecture decisions and notes
    ├── VOICE_GRAMMAR.md
    ├── API_ENDPOINTS.md
    └── DECISIONS.md
```

---

## The Stack
| Layer | Technology | Purpose |
|---|---|---|
| Frontend | Flutter (Dart) | iPhone app — voice input, haptics, dashboard |
| Backend | Flask (Python) | API — game logic, math, diagnostics |
| Database | SQLite → PostgreSQL | Every roll, every session, forever |
| Voice | iOS Speech Framework | On-device, no internet needed |
| Haptics | Apple Watch + CoreHaptics | Blind confirmation at the table |

---

## What Gets Tracked Per Roll
- Left die face
- Right die face
- Total
- Game phase (come-out / point)
- Current point number
- Roll result type (natural, craps, point hit, seven-out, number)
- Timestamp
- Session ID

---

## Analytics (Post-Session Dashboard)
- **SRR** — Seven to Rolls Ratio (your most important number)
- **Axis Control** — Doubles percentage (higher = better on-axis)
- **Signature Numbers** — Which totals you hit above expected frequency
- **Left vs Right Die** — Independent face frequency per die
- **Hot/Cold Streaks** — Longest hand, average hand length
- **Session vs Lifetime** — Today vs all-time trends

---

## Running Locally

### Start the Flask Backend
```bash
cd D:\diceiq\backend
pip install -r requirements.txt
python app.py
```
Backend runs at: http://localhost:5000

### Start the Flutter App
```bash
cd D:\diceiq\frontend
flutter run
```

---

## Project Status
- [ ] Flask API — models, routes, game engine
- [ ] Voice grammar parser
- [ ] Flutter voice input screen
- [ ] Haptic confirmation system
- [ ] Post-session analytics dashboard
- [ ] Apple Watch companion app

---

*Built for Tom — 131-day world cruise, 2026*
