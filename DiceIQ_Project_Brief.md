# DiceIQ.net — Project Brief
*Briefing document for new Claude project session*

---

## What Is DiceIQ

DiceIQ is a SaaS platform for serious craps dice control players. It combines session analytics, performance tracking, AI-powered coaching, training content, and bet strategy into a single mobile-first web application.

The product originated as a personal cruise tracking tool built for Tom (the founder) during a 131-day world cruise on Princess Cruises. During development it became clear the platform had significant commercial potential as no comparable tool exists in the dice control community.

---

## Founder Context

**Tom** is an entrepreneur on a 131-day world cruise with his wife Heather. He has been practicing dice control at the ship's casino, using the cruise as an extended development and testing period. He is not a coder — he is the creative mind and product visionary. Claude is the architect and builder.

Tom has a hearing impairment and wears hearing aids. He approaches gambling analytically, maintaining strict bankroll discipline, targeting modest profits rather than big swings. He plays regularly alongside Jerry, a fellow passenger who uses aggressive betting — providing a useful contrast in approaches.

**ProCalcs** is Tom's existing company. DiceIQ is a separate venture.

---

## The Origin App — Cruise Tracker

A single-file iPhone web app currently live at:
`https://tplatania.github.io/diceiq`

Local file: `D:\diceiq\iphone\index.html`

### What It Does
- Voice-controlled roll entry (speak "3 2" to log left die 3, right die 2)
- Real-time analytics: SRR, BSR, axis control, rotation analysis
- Per dice set breakdown and transpose analysis
- Bankroll tracking (start and end per session)
- Alert system with cooldown and outcome tracking
- Offline-first using localStorage
- Optimized for iPhone, works in Safari

### Why It Can't Be Used At The Table
Princess Cruises prohibits phones and electronic devices at table games. The app pivoted from a live tracking tool to a **post-session analysis tool**. Tom tracks rolls on paper during play, then enters data in his cabin afterward.

### The Paper Tracking System
Tom writes rolls in a small notebook using a simple two-digit system:

```
34        ← come-out roll (flush left)
25        ← come-out, natural winner
35        ← come-out, point is 8
  26      ← point roll (indented)
  33      ← point roll
16        ← new come-out (seven-out happened, back to flush left)
42        ← come-out, point is 6
  51      ← point roll
  25      ← seven out
```

Flush left = come-out roll. Indented = point roll. The game state reconstructs automatically from the math — no labels needed.

### Photo Import Feature (Planned, Not Yet Built)
The next feature to build is photo import — Tom photographs his notebook page, DiceIQ uses Claude vision API to read the handwritten numbers, reconstruct the session, and load all rolls automatically.

---

## The Business Pivot — DiceIQ.net SaaS

### Domain
**DiceIQ.net** — purchased and owned by Tom.
- DiceIQ.com was taken (private financial tool, unrelated)
- .net is legitimate and available

### The Five Founding Decisions
1. **Brand** — DiceIQ.net
2. **Platform** — Mobile-first, works on all phones (web app)
3. **Content strategy** — Original AI-generated/illustrated content Tom owns outright. YouTube embeds/links for free tier. No revenue sharing with coaches or content creators.
4. **Launch strategy** — Full launch (no beta period)
5. **Budget** — Not a constraint

### Target Customer
To be finalized, but likely all three tiers:
- **Beginner** — curious, wants to learn from zero
- **Serious recreational** — plays regularly, wants to improve and track
- **Committed dice controller** — already practicing, wants serious analytics

---

## The Six Core Features

### 1. ElevenLabs Voice
Premium AI voice coaching instead of robotic browser speech. Sounds like a real coach. Requires ElevenLabs API key.

### 2. Custom Dice Sets + Voice Recognition
Users create their own named dice sets (e.g. "Tom's Set"). Define which faces are on-axis. Voice engine automatically recognizes the custom name as a command. Built-in sets: Hardway, All 7s, 3V, 2V.

### 3. Animated Dice Visualization
3D animated dice (Three.js) showing real-time what's happening — axis control, rotation patterns, where the seven lives relative to the active set. Both a teaching tool and a live session visualization.

### 4. Training Library
- **Free tier** — curated YouTube video links (legal — linking/embedding, not copying)
- **Paid tier** — original interactive content: animated diagrams, grip illustrations, throw mechanics, theory explanations
- Topics: grip styles, stance, throw mechanics, set selection theory, bet strategy, bankroll management

### 5. Bet Strategy Engine
Based on live SRR, signature numbers, and bankroll — recommends bet sizing and progression in real time. Genuinely unique. No other tool does this.

### 6. Photo Import / OCR
Claude vision API reads handwritten session sheets. Reconstructs game state automatically. Tom's primary data entry method post-casino.

---

## Monetization Model (Proposed)

| Tier | Price | What They Get |
|---|---|---|
| Free | $0 | Basic tracking, 30-roll limit, YouTube training library |
| Pro | $19/month | Full analytics, photo import, custom dice sets |
| Elite | $39/month | Everything + training content, bet coaching, ElevenLabs voice |
| Academy | $99/month | Elite + live coaching sessions |

---

## Competitive Landscape

| Competitor | Problem |
|---|---|
| BoneTracker | Excel spreadsheet, manual entry, no mobile, no real-time |
| Craps Dice Tracker Pro | Abandoned iOS app, $69.99, bad reviews |
| Controlled Craps Roll Tracker | Web app, no voice, no offline, no analytics depth |
| Golden Touch Craps | $499-999 seminars, no ongoing tracking tool |

**DiceIQ's moat:** The only platform combining analytics + coaching + training + community. Mobile-first. AI-powered. The only tool with voice entry, photo import, rotation analysis, and bet strategy in one place.

---

## The Data Advantage

Every session logged by every user builds an aggregate database. After 10,000 sessions DiceIQ will know:
- Which dice sets produce the best SRR across all players
- Which grip styles correlate with axis control
- Which bet strategies produce the best ROI at different skill levels

**That database becomes the product.** Insights no casino, coach, or book has ever had.

---

## Analytics Engine — Current Capabilities

Already built in the cruise app:

- **SRR** (Seven to Rolls Ratio) — rolls per seven
- **BSR** (Box to Sevens Ratio) — box numbers vs sevens
- **Axis Control %** — doubles percentage vs random baseline
- **Rotation Analysis** — per die (left/right), on-axis vs pitch 90/180 vs off-axis
- **Transpose Analysis** — ranks dice sets by actual performance
- **Per-Set Breakdown** — SRR, BSR, axis per set used
- **Signature Numbers** — which totals run hot/cold vs expected
- **Fatigue Curve** — SRR by 20-roll windows
- **Alert System** — seven spike, SRR drop, axis drop, fatigue window — with cooldown and outcome tracking
- **Bankroll Tracking** — start/end per session, P&L, win rate, cruise total
- **Session History** — all sessions with SRR and P&L

---

## Dice Sets Defined

```
Hardway:  top 3/4, front 2   — 7 requires TWO face movements, best protection
All 7s:   top 3/4, front 4/3 — 7 on all four sides, maximize come-out wins  
3V:       top 3,   front 2/5 — targets 6 and 8
2V:       top 2,   front 4/3 — targets 4 and 10
```

---

## Tom's Playing Style & Strategy

- Uses **Hardway set exclusively** for consistency (one muscle memory, one throw)
- **$10 Pass Line** with **$20 odds** when playing with house money
- Strict stop-loss limits — walks away at predetermined loss threshold
- Takes profits at modest levels — doesn't chase big sessions
- Corrects dealer mistakes even when they would benefit him
- Focused on consistency over complexity

---

## Key Learnings From Cruise Sessions

- Simpler betting strategies outperform complex systems consistently
- Disciplined bankroll management beats intuition every time
- Understanding math behind bets > following popular systems
- Emotional decision-making and FOMO are the primary threats to profit
- Analytical approach + willingness to walk = significant edge over typical players
- Current mechanical issue: dice separating in flight, left die going off-axis

---

## Technical Architecture — Cruise App

- Single HTML file (~1,500 lines)
- Vanilla JavaScript, no frameworks
- localStorage for all data persistence (offline forever)
- Web Speech API for voice recognition
- Speech Synthesis for audio feedback
- GitHub Pages hosting
- Claude API (vision) planned for photo import

---

## Content Strategy Detail

### What Tom Can Create (No Outside Help)
- Written guides on all dice control concepts
- AI-generated illustrations and diagrams
- Interactive tutorials built in the app
- Animated dice visualizations
- Bet strategy calculators

### What Goes In Free Tier
- Curated YouTube links/embeds — best existing dice control content
- Legal: linking and embedding is permitted under YouTube ToS as long as creator hasn't disabled embedding
- Clear attribution to original creators
- Organized by topic (grips, sets, throws, betting, bankroll)

### What Goes In Paid Tiers
- Original DiceIQ content Tom owns outright
- Animated 3D dice demonstrations
- Interactive set selection tool
- Bet strategy engine
- Full analytics suite
- Photo import

---

## Next Immediate Steps

### Cruise App (Short Term)
1. **Photo import** — Claude vision reads handwritten session sheets (partially coded, needs completion)
2. Continue collecting real session data for validation

### DiceIQ.net Product (Medium Term)
1. Define full feature set and user flows
2. Choose tech stack for proper SaaS (authentication, cloud storage, subscriptions)
3. Design mobile-first UI/UX
4. Build training library structure
5. Integrate ElevenLabs voice
6. Build animated dice visualization
7. Develop bet strategy engine
8. Full launch

---

## Questions Still Open

1. Who exactly is the primary target customer? (Beginner / Recreational / Committed)
2. Tech stack for the full SaaS? (React, Next.js, etc.)
3. Payment processor? (Stripe most likely)
4. Community features? (Forum, leaderboards, social)
5. Coaching marketplace? (Third-party coaches listing services)

---

*Document created: March 2026*
*For use in new Claude project session for DiceIQ.net SaaS development*
