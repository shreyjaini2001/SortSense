# SortSense
**AI-Powered Intake Triage for Goodwill Operations Staff**

MIT License | SDG 12 · 8 · 11 | DPG Standard Compliant | MacBook M-series + Gemini API

---

## Quick Start

```bash
# 1. Clone and enter
git clone https://github.com/shreyjaini2001/SortSense.git && cd SortSense

# 2. Add your Gemini API key
cp .env.example .env
# Edit .env and paste your GEMINI_API_KEY

# 3. Run with Docker
docker compose up --build

# Or run locally (dev)
cd backend && pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000

cd frontend && npm install && npm run dev
```

- **Sorter UI:** http://localhost:5173
- **Ops Dashboard:** http://localhost:5173/ops
- **API docs:** http://localhost:8000/docs

---

## How It Works

A fixed camera above the intake tray gives every sorter a **2-second AI decision** — green, blue, or red — for every item, with no training required.

| Colour | Bin | Audience |
|--------|-----|----------|
| 🟢 Green | Reuse | People in urgent need — same-day shelter dispatch |
| 🔵 Blue | Resale | Goodwill floor — auto-priced |
| 🔴 Red | Recycle | E-waste / textile partner pickup |
| 🟡 Yellow | Flag | Human review required |

---

## Signal Logic

### Food
1. **Gemini Vision** — damage, mould, contamination
2. **EasyOCR** — expiry date extraction
3. **Weight Anomaly** — Open Food Facts API vs actual scale weight

### Clothing
1. **Gemini Vision** — condition score 0–100 (tears, stains, fading, completeness)

### Electronics
1. **Gemini Vision** — cracked screens, burn marks, water damage
2. **EasyOCR** — model number extraction
3. **CPSC Recall DB** — public recall safety check

---

## Architecture

```
Webcam (OpenCV) → FastAPI /classify → Triage Orchestrator
                                          ├── food.py      (Vision + OCR + Weight)
                                          ├── clothing.py  (Vision)
                                          └── electronics.py (Vision + OCR + CPSC)
                     ↓ WebSocket
              React Tablet UI (SorterView)
              React Ops Dashboard (OpsView)
                     ↓
              SQLite (→ Postgres in production)
```

---

## DPG Standard Compliance

| # | Indicator | Status |
|---|-----------|--------|
| 1 | SDG Relevance | SDG 12, 8, 11 |
| 2 | Open Licensing | MIT — public from day 1 |
| 3 | Clear Ownership | SortSense Team |
| 4 | Platform Independence | Gemini swappable with CLIP |
| 5 | Documentation | /docs folder |
| 6 | Data Extraction | GET /api/v1/export |
| 7 | Privacy | No PII, frames discarded |
| 8 | Standards | WCAG 2.1 AA, REST |
| 9 | Do No Harm | FLAG state — never force-routes |

---

## Repo Structure

```
SortSense/
├── backend/
│   ├── main.py                  # FastAPI, WebSocket, /classify, /export
│   ├── camera/capture.py        # OpenCV MacBook webcam
│   ├── models/gemini.py         # Gemini 2.0 Flash client
│   ├── models/ocr.py            # EasyOCR wrapper
│   └── triage/
│       ├── orchestrator.py      # Category router
│       ├── food.py
│       ├── clothing.py
│       └── electronics.py
├── frontend/src/
│   ├── SorterView.jsx           # Sorter tablet UI
│   └── OpsView.jsx              # Ops dashboard
├── docs/
├── docker-compose.yml
└── LICENSE (MIT)
```

---

*Built for the sorter. Open for the world.*
