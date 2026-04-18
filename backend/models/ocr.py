import easyocr
import base64
import numpy as np
from PIL import Image
import io
import re
from datetime import date, datetime

_reader = None


def get_reader():
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(["en"], gpu=False)
    return _reader


def _b64_to_numpy(b64: str) -> np.ndarray:
    raw = base64.b64decode(b64)
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    return np.array(img)


def extract_text(b64_image: str) -> list[str]:
    """Extract all text strings from image."""
    reader = get_reader()
    arr = _b64_to_numpy(b64_image)
    results = reader.readtext(arr, detail=0)
    return results


def extract_expiry_date(b64_image: str) -> dict:
    """Extract expiry date from food packaging label."""
    texts = extract_text(b64_image)
    full_text = " ".join(texts)

    patterns = [
        r'\b(EXP|BEST BY|USE BY|BB|BEST BEFORE)[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b',
        r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b',
        r'\b(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\s+(\d{1,2})\s*,?\s*(\d{4})\b',
    ]

    for pattern in patterns:
        match = re.search(pattern, full_text, re.IGNORECASE)
        if match:
            raw_date = match.group(0)
            return {"found": True, "raw": raw_date, "expired": _is_expired(raw_date)}

    return {"found": False, "raw": None, "expired": None}


def extract_model_number(b64_image: str) -> dict:
    """Extract model number from electronics label."""
    texts = extract_text(b64_image)
    full_text = " ".join(texts)

    patterns = [
        r'\b(MODEL|MDL|MOD)[:\s#]*([A-Z0-9\-]{4,20})\b',
        r'\b([A-Z]{1,4}[-]?[0-9]{2,6}[-]?[A-Z0-9]{0,6})\b',
    ]

    for pattern in patterns:
        match = re.search(pattern, full_text, re.IGNORECASE)
        if match:
            model = match.groups()[-1].strip()
            return {"found": True, "model_number": model}

    return {"found": False, "model_number": None}


def _is_expired(date_str: str) -> bool:
    today = date.today()
    formats = ["%m/%d/%Y", "%m-%d-%Y", "%m/%d/%y", "%m-%d-%y", "%d/%m/%Y", "%d-%m-%Y"]
    for fmt in formats:
        try:
            parsed = datetime.strptime(date_str.split()[-1], fmt).date()
            return parsed < today
        except ValueError:
            continue
    return False
