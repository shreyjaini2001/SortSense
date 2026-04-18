import os
import base64
import google.generativeai as genai
from PIL import Image
import io

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
_model = genai.GenerativeModel("gemini-2.0-flash-exp")


def _image_from_b64(b64: str) -> Image.Image:
    raw = base64.b64decode(b64)
    return Image.open(io.BytesIO(raw))


def classify_category(b64_image: str) -> dict:
    """Detect item category: food | clothing | electronics | unknown."""
    img = _image_from_b64(b64_image)
    prompt = (
        "Look at this donated item. Classify it into exactly one category: "
        "'food', 'clothing', or 'electronics'. "
        "Reply with JSON only: {\"category\": \"<value>\", \"confidence\": <0.0-1.0>}"
    )
    response = _model.generate_content([prompt, img])
    import json, re
    text = response.text.strip()
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return json.loads(match.group())
    return {"category": "unknown", "confidence": 0.0}


def analyze_food(b64_image: str) -> dict:
    """Vision analysis for food items."""
    img = _image_from_b64(b64_image)
    prompt = (
        "Analyze this donated food item. Check for: packaging damage, visible mould, "
        "open containers, foreign contamination, and overall safety. "
        "Reply with JSON only: "
        "{\"safe\": <bool>, \"condition\": \"<good|fair|poor>\", "
        "\"issues\": [<list of issues>], \"confidence\": <0.0-1.0>, "
        "\"reasoning\": \"<one sentence>\"}"
    )
    response = _model.generate_content([prompt, img])
    import json, re
    text = response.text.strip()
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return json.loads(match.group())
    return {"safe": False, "condition": "poor", "issues": [], "confidence": 0.0, "reasoning": "Could not analyze"}


def analyze_clothing(b64_image: str) -> dict:
    """Vision analysis for clothing items — no MobileNet, Gemini only."""
    img = _image_from_b64(b64_image)
    prompt = (
        "Analyze this donated clothing or textile item. Assess: tears, stains, missing buttons, "
        "significant fading, overall wear. Also note brand if visible. "
        "Give a condition score 0-100 (100=like new, 0=destroyed). "
        "Reply with JSON only: "
        "{\"condition_score\": <0-100>, \"issues\": [<list>], \"brand\": \"<brand or null>\", "
        "\"complete\": <bool>, \"confidence\": <0.0-1.0>, \"reasoning\": \"<one sentence>\"}"
    )
    response = _model.generate_content([prompt, img])
    import json, re
    text = response.text.strip()
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return json.loads(match.group())
    return {"condition_score": 0, "issues": [], "brand": None, "complete": False, "confidence": 0.0, "reasoning": "Could not analyze"}


def analyze_electronics(b64_image: str) -> dict:
    """Vision analysis for electronics/appliances."""
    img = _image_from_b64(b64_image)
    prompt = (
        "Analyze this donated electronic item. Check for: cracked screens, missing components, "
        "burnt marks, water damage indicators, physical damage. Estimate functional probability. "
        "Reply with JSON only: "
        "{\"functional_probability\": <0.0-1.0>, \"issues\": [<list>], "
        "\"confidence\": <0.0-1.0>, \"reasoning\": \"<one sentence>\"}"
    )
    response = _model.generate_content([prompt, img])
    import json, re
    text = response.text.strip()
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return json.loads(match.group())
    return {"functional_probability": 0.0, "issues": [], "confidence": 0.0, "reasoning": "Could not analyze"}
