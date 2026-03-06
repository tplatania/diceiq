# DiceIQ — How To Get This On Your iPhone

## One-Time Setup (5 minutes)

### Step 1 — Open the file in VS Code
Navigate to D:\diceiq\iphone\index.html

### Step 2 — Run a simple local server
Open VS Code terminal and type:
    cd D:\diceiq\iphone
    python -m http.server 8080

You'll see: "Serving HTTP on 0.0.0.0 port 8080"

### Step 3 — Find your Windows IP address
Open a NEW terminal tab and type:
    ipconfig

Look for "IPv4 Address" — it will look like 192.168.1.XX

### Step 4 — Open on iPhone
Make sure iPhone is on same WiFi as laptop.
Open Safari on iPhone.
Type: http://192.168.1.XX:8080
(replace XX with your actual numbers)

### Step 5 — Add to Home Screen
In Safari tap the Share button (box with arrow pointing up)
Tap "Add to Home Screen"
Tap "Add"

DiceIQ now appears on your home screen like a real app.
It is now cached and works OFFLINE — no WiFi needed.

## Every Day After That
Just tap the DiceIQ icon on your home screen.
No laptop needed. No WiFi needed. Works anywhere.

## To Back Up Your Data
Open the app → STATS → EXPORT SESSION DATA
A JSON file downloads — AirDrop or email it to yourself.

## Important iPhone Setting
Go to Settings → Display & Brightness → Auto-Lock → Set to NEVER
This keeps the screen awake while you play.
(Remember to set it back after your session to save battery)
