# DiceIQ — Updated Architecture
# Web-first. Flask serves everything. iPhone opens Safari.
# No Flutter. No App Store. No Mac needed.

## What Changed
- Frontend is now HTML/CSS/JavaScript served by Flask
- iPhone opens Safari, types in the local IP address once
- Same WiFi network = instant connection
- Voice, haptics, audio all work natively in Safari on iOS

## How It Runs
1. Tom opens VS Code terminal
2. Runs: cd D:\diceiq\backend && python app.py
3. Flask starts at http://YOUR-IP:5000
4. iPhone opens Safari → types that address → app loads
5. Done. No installs. No App Store. No Mac.

## File Structure (Updated)
D:\diceiq\
├── backend\
│   ├── app.py              ← Start Flask here
│   ├── models.py           ← Database models
│   ├── engine.py           ← Game logic + diagnostics
│   ├── routes.py           ← API endpoints
│   ├── requirements.txt    ← Python packages
│   ├── templates\
│   │   └── index.html      ← The web app UI
│   ├── static\
│   │   ├── app.js          ← Voice + game logic
│   │   └── style.css       ← Dark casino theme
│   └── database\
│       └── diceiq.db       ← Every roll stored forever
├── docs\
└── README.md
