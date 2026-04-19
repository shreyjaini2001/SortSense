import os
import asyncio
import httpx
from backend.models import gemini, ocr
from backend.triage.constants import CONFIDENCE_THRESHOLD
from backend.triage.utils import cant_see_item

CPSC_API_URL = os.getenv("CPSC_API_URL", "https://www.saferproducts.gov/RestWebServices/Recall")

_CANT_SEE_PHRASES = ["no electronic", "not visible", "no item", "person", "not an electronic"]


async def analyze(b64_image: str) -> dict:
    vision, model_info = await asyncio.gather(
        asyncio.to_thread(gemini.analyze_electronics, b64_image),
        asyncio.to_thread(ocr.extract_model_number, b64_image),
    )

    recalled = False
    recall_note = None
    if model_info.get("found"):
        recall_result = await _check_cpsc_recall(model_info["model_number"])
        recalled = recall_result.get("recalled", False)
        recall_note = recall_result.get("note")

    signals = {
        "vision": vision,
        "model_number": model_info,
        "recalled": recalled,
        "recall_note": recall_note,
    }

    functional_prob = vision.get("functional_probability", 0.0)
    confidence = vision.get("confidence", 0.0)

    if cant_see_item(vision.get("issues", []), _CANT_SEE_PHRASES):
        return {
            "category": "electronics",
            "bin": "flag",
            "confidence": confidence,
            "functional_probability": functional_prob,
            "reason": "Place the electronic item label-side up in front of the camera.",
            "signals": signals,
        }

    if confidence < CONFIDENCE_THRESHOLD:
        bin_decision = "flag"
        reason = "Item needs human review — confidence too low to route automatically."
    elif recalled:
        bin_decision = "recycle"
        reason = f"Item flagged by CPSC recall database — {recall_note or 'routed to e-waste partner'}."
    elif functional_prob >= 0.75:
        bin_decision = "resale"
        reason = _build_reason("resale", vision, functional_prob)
    elif functional_prob >= 0.40:
        bin_decision = "reuse"
        reason = _build_reason("reuse", vision, functional_prob)
    else:
        bin_decision = "recycle"
        reason = _build_reason("recycle", vision, functional_prob)

    return {
        "category": "electronics",
        "bin": bin_decision,
        "confidence": confidence,
        "functional_probability": functional_prob,
        "reason": reason,
        "signals": signals,
    }


async def _check_cpsc_recall(model_number: str) -> dict:
    try:
        async with httpx.AsyncClient(timeout=6.0, follow_redirects=True) as client:
            resp = await client.get(
                CPSC_API_URL,
                params={"format": "json", "query": model_number, "limit": 1},
            )
            if resp.status_code == 200:
                data = resp.json()
                recalls = data if isinstance(data, list) else data.get("results", [])
                if recalls:
                    return {"recalled": True, "note": recalls[0].get("Title", "Recall found")}
    except Exception:
        pass
    return {"recalled": False, "note": None}


def _build_reason(bin_decision: str, vision: dict, functional_prob: float) -> str:
    pct = int(functional_prob * 100)
    issues = vision.get("issues", [])
    issue_note = f" Issues: {', '.join(issues)}." if issues else ""

    if bin_decision == "resale":
        return f"Likely functional ({pct}% probability) — ready for Goodwill floor. {vision.get('reasoning', '')}"
    elif bin_decision == "reuse":
        return f"Partially functional ({pct}%) — routed to repair/reuse partner.{issue_note}"
    else:
        return f"Non-functional ({pct}%) — routed to e-waste recycling.{issue_note}"
