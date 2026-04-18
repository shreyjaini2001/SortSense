# System Architecture

## Data Flow

1. Sorter places item on tray — webcam captures frame via OpenCV
2. Frame sent to FastAPI `/classify` endpoint via WebSocket
3. Triage orchestrator detects category (Gemini vision)
4. Category-specific pipeline fires (vision + OCR + external signals)
5. Confidence computed: ≥70% → bin decision, <70% → FLAG
6. WebSocket pushes result to React tablet UI in <2 seconds
7. Result logged to SQLite with full signal breakdown

## Component Map

```
frontend/src/SorterView.jsx   ←→  WebSocket  ←→  backend/main.py
frontend/src/OpsView.jsx      ←→  REST API   ←→  /api/v1/stats
                                               ←→  /api/v1/export

backend/main.py → triage/orchestrator.py
                      ├── triage/food.py        → gemini + ocr + Open Food Facts
                      ├── triage/clothing.py    → gemini
                      └── triage/electronics.py → gemini + ocr + CPSC API

backend/camera/capture.py  → OpenCV device_index=0 (MacBook FaceTime HD)
backend/db/models.py       → SQLAlchemy → SQLite (swappable to Postgres)
```
