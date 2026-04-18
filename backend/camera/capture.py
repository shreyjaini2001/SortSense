import cv2
import base64
import numpy as np
from PIL import Image
import io

_camera = None


def get_camera():
    global _camera
    if _camera is None or not _camera.isOpened():
        _camera = cv2.VideoCapture(0)
        # Fixed exposure for consistent MacBook webcam output
        _camera.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
        _camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        _camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    return _camera


def capture_frame() -> tuple[bytes, str]:
    """Capture a single frame. Returns (raw_bytes, base64_jpeg)."""
    cam = get_camera()
    ret, frame = cam.read()
    if not ret:
        raise RuntimeError("Failed to capture frame from webcam")

    _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
    raw = buffer.tobytes()
    b64 = base64.b64encode(raw).decode("utf-8")
    return raw, b64


def release_camera():
    global _camera
    if _camera and _camera.isOpened():
        _camera.release()
        _camera = None
