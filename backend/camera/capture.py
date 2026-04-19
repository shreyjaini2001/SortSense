import base64
import subprocess
import tempfile
import os


def capture_frame() -> tuple[bytes, str]:
    """
    Capture a single frame via imagesnap (macOS native AVFoundation).
    Returns (raw_jpeg_bytes, base64_jpeg_string).
    """
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        subprocess.run(
            ["imagesnap", "-w", "1.5", tmp_path],
            check=True,
            capture_output=True,
        )
        with open(tmp_path, "rb") as f:
            raw = f.read()
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

    if not raw:
        raise RuntimeError("imagesnap returned an empty frame.")

    b64 = base64.b64encode(raw).decode("utf-8")
    return raw, b64


def release_camera():
    pass  # imagesnap opens/closes the camera per-capture; nothing to release
