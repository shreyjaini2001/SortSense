from backend.models import gemini
from backend.triage import food, clothing, electronics, general
from backend.triage.constants import CONFIDENCE_THRESHOLD


async def classify(b64_image: str, weight_grams: float | None = None) -> dict:
    """
    Entry point for all triage decisions.
    Step 1: Detect category via Gemini vision.
    Step 2: Route to category-specific signal pipeline.
    """
    category_result = gemini.classify_category(b64_image)
    category = category_result.get("category", "unknown")
    category_confidence = category_result.get("confidence", 0.0)

    if category_confidence < CONFIDENCE_THRESHOLD:
        return {
            "category": "unknown",
            "bin": "flag",
            "confidence": category_confidence,
            "reason": "Could not identify item category — please show the item more clearly.",
            "signals": {"category_detection": category_result},
        }

    if category == "food":
        result = await food.analyze(b64_image, weight_grams)
    elif category == "clothing":
        result = await clothing.analyze(b64_image)
    elif category == "electronics":
        result = await electronics.analyze(b64_image)
    elif category == "general":
        result = await general.analyze(b64_image, category_result.get("item_name", "item"))
    else:
        result = {
            "category": "unknown",
            "bin": "flag",
            "confidence": 0.0,
            "reason": "Item category not recognised — please seek supervisor review.",
            "signals": {},
        }

    result["signals"]["category_detection"] = category_result
    return result
