import os
import re
import asyncio
import httpx
from backend.models import gemini, ocr
from backend.triage.constants import CONFIDENCE_THRESHOLD
from backend.triage.utils import cant_see_item

OFF_API_URL = os.getenv("OFF_API_URL", "https://world.openfoodfacts.org/api/v2")

_CANT_SEE_PHRASES = ["no food", "not visible", "no item", "person", "not a food"]


async def analyze(b64_image: str, weight_grams: float | None = None) -> dict:
    vision, expiry = await asyncio.gather(
        asyncio.to_thread(gemini.analyze_food, b64_image),
        asyncio.to_thread(ocr.extract_expiry_date, b64_image),
    )

    weight_anomaly = False
    weight_note = None
    if weight_grams is not None:
        weight_result = await _check_weight_anomaly(weight_grams)
        weight_anomaly = weight_result.get("anomaly", False)
        weight_note = weight_result.get("note")

    signals = {
        "vision": vision,
        "expiry": expiry,
        "weight_anomaly": weight_anomaly,
        "weight_note": weight_note,
    }

    confidence = vision.get("confidence", 0.0)

    if cant_see_item(vision.get("issues", []), _CANT_SEE_PHRASES):
        return {
            "category": "food",
            "bin": "flag",
            "confidence": confidence,
            "reason": "Place the food item label-side up in front of the camera.",
            "signals": signals,
        }

    if not vision.get("safe") or expiry.get("expired") or weight_anomaly:
        if confidence >= CONFIDENCE_THRESHOLD:
            bin_decision = "recycle"
            reason = _build_reason("recycle", vision, expiry, weight_anomaly)
        else:
            bin_decision = "flag"
            reason = "Item needs human review — confidence too low to route automatically."
    else:
        if confidence >= CONFIDENCE_THRESHOLD:
            bin_decision = "reuse"
            reason = _build_reason("reuse", vision, expiry, weight_anomaly)
        else:
            bin_decision = "flag"
            reason = "Item needs human review — confidence too low to route automatically."

    return {
        "category": "food",
        "bin": bin_decision,
        "confidence": confidence,
        "reason": reason,
        "signals": signals,
    }


async def _check_weight_anomaly(actual_weight: float) -> dict:
    try:
        async with httpx.AsyncClient(timeout=6.0, follow_redirects=True) as client:
            resp = await client.get(
                f"{OFF_API_URL}/search",
                params={"fields": "product_name,quantity", "page_size": 1},
            )
            if resp.status_code == 200:
                products = resp.json().get("products", [])
                if products:
                    expected = _parse_grams(products[0].get("quantity", ""))
                    if expected and abs(actual_weight - expected) / expected > 0.20:
                        return {"anomaly": True, "note": f"Expected ~{expected}g, got {actual_weight}g"}
    except Exception:
        pass
    return {"anomaly": False, "note": None}


def _parse_grams(quantity_str: str) -> float | None:
    match = re.search(r'(\d+\.?\d*)\s*(g|kg|oz|lb)', quantity_str, re.IGNORECASE)
    if not match:
        return None
    value, unit = float(match.group(1)), match.group(2).lower()
    return value * {"g": 1, "kg": 1000, "oz": 28.35, "lb": 453.59}.get(unit, 1)


def _build_reason(bin_decision: str, vision: dict, expiry: dict, weight_anomaly: bool) -> str:
    if bin_decision == "reuse":
        return f"Food item appears safe — {vision.get('reasoning', 'no visible issues detected')}."
    parts = []
    if vision.get("issues"):
        parts.append(f"vision issues: {', '.join(vision['issues'])}")
    if expiry.get("expired"):
        parts.append("past expiry date")
    if weight_anomaly:
        parts.append("weight anomaly detected")
    return f"Routed to recycle — {'; '.join(parts)}." if parts else "Item does not meet safety standards."
