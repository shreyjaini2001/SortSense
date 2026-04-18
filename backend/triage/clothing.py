from backend.models import gemini

CONFIDENCE_THRESHOLD = 0.70


async def analyze(b64_image: str) -> dict:
    """
    Multi-signal clothing triage (Gemini vision only — no MobileNet).
    Signal 1: Gemini vision — condition score 0-100, tears/stains/fading/completeness
    Routing: score >= 70 → resale | 40-69 → reuse | < 40 → recycle
    """
    vision = gemini.analyze_clothing(b64_image)

    condition_score = vision.get("condition_score", 0)
    confidence = vision.get("confidence", 0.0)

    if confidence < CONFIDENCE_THRESHOLD:
        bin_decision = "flag"
        reason = "Item needs human review — confidence too low to route automatically."
    elif condition_score >= 70:
        bin_decision = "resale"
        reason = _build_reason("resale", vision, condition_score)
    elif condition_score >= 40:
        bin_decision = "reuse"
        reason = _build_reason("reuse", vision, condition_score)
    else:
        bin_decision = "recycle"
        reason = _build_reason("recycle", vision, condition_score)

    return {
        "category": "clothing",
        "bin": bin_decision,
        "confidence": confidence,
        "condition_score": condition_score,
        "reason": reason,
        "signals": {"vision": vision},
    }


def _build_reason(bin_decision: str, vision: dict, score: int) -> str:
    reasoning = vision.get("reasoning", "")
    issues = vision.get("issues", [])
    brand = vision.get("brand")
    brand_note = f" ({brand})" if brand else ""

    if bin_decision == "resale":
        return f"Good condition{brand_note} (score {score}/100) — ready for Goodwill floor. {reasoning}"
    elif bin_decision == "reuse":
        issue_note = f" Issues: {', '.join(issues)}." if issues else ""
        return f"Usable condition (score {score}/100) — routed to someone in need.{issue_note}"
    else:
        issue_note = f" Issues: {', '.join(issues)}." if issues else ""
        return f"Poor condition (score {score}/100) — routed to textile recycling partner.{issue_note}"
