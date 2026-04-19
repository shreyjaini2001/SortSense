import asyncio
from backend.models import gemini
from backend.triage.constants import CONFIDENCE_THRESHOLD
from backend.triage.utils import cant_see_item

_CANT_SEE_PHRASES = ["not visible", "no item", "person", "not a cloth", "not textile", "not clearly"]


async def analyze(b64_image: str) -> dict:
    vision = await asyncio.to_thread(gemini.analyze_clothing, b64_image)

    condition_score = vision.get("condition_score", 0)
    confidence = vision.get("confidence", 0.0)

    if cant_see_item(vision.get("issues", []), _CANT_SEE_PHRASES) or confidence < CONFIDENCE_THRESHOLD:
        return {
            "category": "clothing",
            "bin": "flag",
            "confidence": confidence,
            "condition_score": condition_score,
            "reason": "Place the item flat in front of the camera — item not clearly visible for assessment.",
            "signals": {"vision": vision},
        }

    if condition_score >= 70:
        bin_decision = "resale"
    elif condition_score >= 40:
        bin_decision = "reuse"
    else:
        bin_decision = "recycle"

    return {
        "category": "clothing",
        "bin": bin_decision,
        "confidence": confidence,
        "condition_score": condition_score,
        "reason": _build_reason(bin_decision, vision, condition_score),
        "signals": {"vision": vision},
    }


def _build_reason(bin_decision: str, vision: dict, score: int) -> str:
    issues = vision.get("issues", [])
    brand = vision.get("brand")
    item_type = vision.get("item_type", "clothing item")
    graphic = vision.get("print_or_graphic")
    color = vision.get("color")

    parts = [p for p in [color, brand, item_type] if p]
    description = " ".join(parts) if parts else "clothing item"
    graphic_note = f" with {graphic}" if graphic else ""
    issue_note = f" Issues: {', '.join(issues)}." if issues else ""

    if bin_decision == "resale":
        return f"{description.capitalize()}{graphic_note} in good condition (score {score}/100) — ready for Goodwill floor. {vision.get('reasoning', '')}"
    elif bin_decision == "reuse":
        return f"{description.capitalize()}{graphic_note} (score {score}/100) — routed to someone in need.{issue_note}"
    else:
        return f"{description.capitalize()}{graphic_note} (score {score}/100) — too worn for resale.{issue_note}"
