import os
import json
import re
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

_client = None
MODEL = "Qwen/Qwen3-VL-30B-A3B-Instruct"


def get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.getenv("FEATHERLESS_API_KEY")
        if not api_key:
            raise RuntimeError("FEATHERLESS_API_KEY not set in .env")
        _client = OpenAI(
            api_key=api_key,
            base_url="https://api.featherless.ai/v1",
        )
    return _client


def _vision_call(prompt: str, b64_image: str) -> str:
    """Send a prompt + image to the vision model, return raw text response."""
    response = get_client().chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"},
                    },
                ],
            }
        ],
        max_tokens=512,
        temperature=0.1,
    )
    return response.choices[0].message.content.strip()


def _parse_json(text: str) -> dict | None:
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            return None
    return None


def classify_category(b64_image: str) -> dict:
    """Detect item category: food | clothing | electronics | general | unknown."""
    prompt = (
        "Look at this donated item and classify it into exactly one category:\n"
        "- 'food': any food, drink, packaged edibles, canned goods\n"
        "- 'clothing': clothes, shoes, bags, accessories, textiles\n"
        "- 'electronics': phones, laptops, appliances, cables, anything with a plug or battery\n"
        "- 'general': everything else — books, toys, tools, kitchenware, stationery, pens, paper, "
        "games, furniture, sporting goods, décor, office supplies\n\n"
        "Also name the item and estimate condition.\n"
        "Reply with JSON only, no markdown, example:\n"
        "{\"category\": \"general\", \"item_name\": \"pen and notepad\", "
        "\"condition\": \"good\", \"confidence\": 0.95}"
    )
    text = _vision_call(prompt, b64_image)
    result = _parse_json(text)
    if result:
        return result
    return {"category": "unknown", "item_name": "unknown", "condition": "unknown", "confidence": 0.0}


def analyze_food(b64_image: str) -> dict:
    """Vision analysis for food items."""
    prompt = (
        "Analyze this donated food item. Check for: packaging damage, visible mould, "
        "open containers, foreign contamination, and overall safety. "
        "Reply with JSON only, no markdown, example: "
        "{\"safe\": true, \"condition\": \"good\", "
        "\"issues\": [], \"confidence\": 0.92, "
        "\"reasoning\": \"Packaging intact, no visible damage.\"}"
    )
    text = _vision_call(prompt, b64_image)
    result = _parse_json(text)
    if result:
        return result
    return {"safe": False, "condition": "poor", "issues": [], "confidence": 0.0, "reasoning": "Could not analyze"}


def analyze_clothing(b64_image: str) -> dict:
    """Vision analysis for clothing items."""
    prompt = (
        "Analyze this donated clothing or textile item. Assess: tears, stains, missing buttons, "
        "significant fading, overall wear. Also note brand if visible. "
        "Give a condition score 0-100 (100=like new, 0=destroyed). "
        "Reply with JSON only, no markdown, example: "
        "{\"condition_score\": 75, \"issues\": [\"minor fading\"], \"brand\": \"Nike\", "
        "\"complete\": true, \"confidence\": 0.88, \"reasoning\": \"Good condition with minor wear.\"}"
    )
    text = _vision_call(prompt, b64_image)
    result = _parse_json(text)
    if result:
        return result
    return {"condition_score": 0, "issues": [], "brand": None, "complete": False, "confidence": 0.0, "reasoning": "Could not analyze"}


def analyze_general(b64_image: str) -> dict:
    """Vision analysis for general goods (books, toys, tools, stationery, etc.)."""
    prompt = (
        "Analyze this donated item. Assess its overall condition for resale at a Goodwill store. "
        "Give a condition score 0-100 (100=like new, 0=destroyed/unusable). "
        "Reply with JSON only, no markdown, example: "
        "{\"condition_score\": 80, \"item_name\": \"hardcover book\", "
        "\"issues\": [], \"confidence\": 0.90, \"reasoning\": \"Book in great condition, no torn pages.\"}"
    )
    text = _vision_call(prompt, b64_image)
    result = _parse_json(text)
    if result:
        return result
    return {"condition_score": 50, "item_name": "item", "issues": [], "confidence": 0.0, "reasoning": "Could not analyze"}


def analyze_electronics(b64_image: str) -> dict:
    """Vision analysis for electronics/appliances."""
    prompt = (
        "Analyze this donated electronic item. Check for: cracked screens, missing components, "
        "burnt marks, water damage indicators, physical damage. Estimate functional probability. "
        "Reply with JSON only, no markdown, example: "
        "{\"functional_probability\": 0.80, \"issues\": [\"minor scratch\"], "
        "\"confidence\": 0.85, \"reasoning\": \"Device appears intact and likely functional.\"}"
    )
    text = _vision_call(prompt, b64_image)
    result = _parse_json(text)
    if result:
        return result
    return {"functional_probability": 0.0, "issues": [], "confidence": 0.0, "reasoning": "Could not analyze"}
