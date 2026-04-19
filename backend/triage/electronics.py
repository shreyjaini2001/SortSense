import os
import httpx
from backend.models import gemini, ocr

CPSC_API_URL = os.getenv("CPSC_API_URL", "https://www.saferproducts.gov/RestWebServices/Recall")
CONFIDENCE_THRESHOLD = 0.70


async def analyze(b64_image: str) -> dict:
    """
    Multi-signal electronics triage.
    Signal 1: Gemini vision — physical damage assessment
    Signal 2: EasyOCR model number extraction
    Signal 3: CPSC recall database lookup
    """
    vision = gemini.analyze_electronics(b64_image)
    model_info = ocr.extract_model_number(b64_image)

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
    issues = vision.get("issues", [])

    cant_see = any(
        phrase in " ".join(issues).lower()
        for phrase in ["no electronic", "not visible", "no item", "person", "not an electronic"]
    )
    if cant_see:
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
    """Check CPSC public recall database for the given model number."""
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
    reasoning = vision.get("reasoning", "")
    issues = vision.get("issues", [])
    pct = int(functional_prob * 100)

    if bin_decision == "resale":
        return f"Likely functional ({pct}% probability) — ready for Goodwill floor. {reasoning}"
    elif bin_decision == "reuse":
        issue_note = f" Issues: {', '.join(issues)}." if issues else ""
        return f"Partially functional ({pct}%) — routed to repair/reuse partner.{issue_note}"
    else:
        issue_note = f" Issues: {', '.join(issues)}." if issues else ""
        return f"Non-functional ({pct}%) — routed to e-waste recycling.{issue_note}"
