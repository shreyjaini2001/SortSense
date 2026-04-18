import os
import json
import uuid
from datetime import datetime, date
from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.camera.capture import capture_frame, release_camera
from backend.triage.orchestrator import classify
from backend.db.models import init_db, get_db, TriageLog


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
    release_camera()


app = FastAPI(title="SortSense API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ClassifyRequest(BaseModel):
    weight_grams: float | None = None
    session_id: str | None = None


class ClassifyFromImageRequest(BaseModel):
    b64_image: str
    weight_grams: float | None = None
    session_id: str | None = None


@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@app.post("/classify")
async def classify_item(request: ClassifyRequest, db: Session = Depends(get_db)):
    """Capture a webcam frame and classify the item."""
    _, b64 = capture_frame()
    result = await classify(b64, request.weight_grams)
    _log_result(db, result, request.weight_grams, request.session_id or str(uuid.uuid4()))
    return result


@app.post("/classify/image")
async def classify_from_image(request: ClassifyFromImageRequest, db: Session = Depends(get_db)):
    """Classify from a base64 image (for testing / tablet capture fallback)."""
    result = await classify(request.b64_image, request.weight_grams)
    _log_result(db, result, request.weight_grams, request.session_id or str(uuid.uuid4()))
    return result


@app.get("/api/v1/export")
async def export_data(db: Session = Depends(get_db)):
    """Export all triage session data as JSON — DPG Indicator 6."""
    logs = db.query(TriageLog).all()
    return JSONResponse(content={
        "export_date": date.today().isoformat(),
        "total_items": len(logs),
        "items": [
            {
                "id": log.id,
                "timestamp": log.timestamp.isoformat(),
                "category": log.category,
                "bin": log.bin,
                "confidence": log.confidence,
                "reason": log.reason,
                "weight_grams": log.weight_grams,
                "session_id": log.session_id,
                "signal_breakdown": log.signal_breakdown,
            }
            for log in logs
        ],
    })


@app.get("/api/v1/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Today's triage counts for the ops dashboard."""
    today = date.today()
    logs = db.query(TriageLog).filter(
        TriageLog.timestamp >= datetime(today.year, today.month, today.day)
    ).all()

    counts = {"reuse": 0, "resale": 0, "recycle": 0, "flag": 0}
    by_category = {"food": 0, "clothing": 0, "electronics": 0, "unknown": 0}

    for log in logs:
        if log.bin in counts:
            counts[log.bin] += 1
        if log.category in by_category:
            by_category[log.category] += 1

    return {
        "date": today.isoformat(),
        "total": len(logs),
        "by_bin": counts,
        "by_category": by_category,
        "flag_rate": round(counts["flag"] / max(len(logs), 1), 3),
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    """
    WebSocket for real-time sorter UI.
    Client sends: {"action": "classify", "weight_grams": <float|null>, "session_id": "<str>"}
    Server pushes: triage result JSON
    """
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            action = payload.get("action")

            if action == "classify":
                weight = payload.get("weight_grams")
                session_id = payload.get("session_id", str(uuid.uuid4()))
                b64_image = payload.get("b64_image")

                if b64_image:
                    result = await classify(b64_image, weight)
                else:
                    _, b64 = capture_frame()
                    result = await classify(b64, weight)

                _log_result(db, result, weight, session_id)
                await websocket.send_text(json.dumps(result))

            elif action == "stats":
                stats_response = await get_stats(db)
                await websocket.send_text(json.dumps(stats_response))

    except WebSocketDisconnect:
        pass


def _log_result(db: Session, result: dict, weight: float | None, session_id: str):
    log = TriageLog(
        category=result.get("category"),
        bin=result.get("bin"),
        confidence=result.get("confidence"),
        reason=result.get("reason"),
        signal_breakdown=result.get("signals"),
        weight_grams=weight,
        session_id=session_id,
    )
    db.add(log)
    db.commit()
