import asyncio
from backend.models import gemini
from backend.triage.constants import CONFIDENCE_THRESHOLD
from backend.triage.utils import cant_see_item

_CANT_SEE_PHRASES = ["not visible", "no item", "person", "cannot see", "no object", "empty"]


async def analyze(b64_image: str, item_name: str = "item") -> dict:
    vision = await asyncio.to_thread(gemini.analyze_general, b64_image)

    condition_score = vision.get("condition_score", 50)
    confidence = vision.get("confidence", 0.0)
    detected_name = vision.get("item_name") or item_name

    if cant_see_item(vision.get("issues", []), _CANT_SEE_PHRASES) or confidence < CONFIDENCE_THRESHOLD:
        return {
            "category": "general",
            "bin": "flag",
            "confidence": confidence,
            "condition_score": condition_score,
            "reason": "Place the item clearly in front of the camera for assessment.",
            "signals": {"vision": vision},
        }

    if condition_score >= 65:
        bin_decision = "resale"
    elif condition_score >= 35:
        bin_decision = "reuse"
    else:
        bin_decision = "recycle"

    return {
        "category": "general",
        "bin": bin_decision,
        "confidence": confidence,
        "condition_score": condition_score,
        "reason": _build_reason(bin_decision, detected_name, vision, condition_score),
        "signals": {"vision": vision},
    }


def _build_reason(bin_decision: str, item_name: str, vision: dict, score: int) -> str:
    issues = vision.get("issues", [])
    issue_note = f" Issues: {', '.join(issues)}." if issues else ""

    if bin_decision == "resale":
        return f"{item_name.capitalize()} in good condition (score {score}/100) — ready for Goodwill floor. {vision.get('reasoning', '')}"
    elif bin_decision == "reuse":
        return f"{item_name.capitalize()} usable condition (score {score}/100) — routed to reuse partner.{issue_note}"
    else:
        return f"{item_name.capitalize()} too worn for resale or reuse (score {score}/100) — routed to recycling.{issue_note}"
