import base64
import os
import struct
import sys
import zlib
import requests

# Retrieve API key securely from environment variables (never hardcode secrets)
ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY")
INFERENCE_SERVER_URL = os.getenv("INFERENCE_SERVER_URL", "http://localhost:9001")
MODEL_ID = os.getenv("ROBOFLOW_MODEL_ID", "yolov8n-640")


def generate_valid_png_b64(width: int = 64, height: int = 64) -> str:
    """Generate a valid in-memory PNG image encoded as Base64 (prevents SSRF from external URLs)."""
    raw_data = b"".join(b"\x00" + b"\x00\x00\xff" * width for _ in range(height))
    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack("!I", len(data)) + tag + data + struct.pack("!I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    ihdr = struct.pack("!IIBBBBB", width, height, 8, 2, 0, 0, 0)
    png_bytes = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw_data)) + chunk(b"IEND", b"")
    return base64.b64encode(png_bytes).decode("ascii")


def run_inference():
    if not ROBOFLOW_API_KEY:
        print("Error: ROBOFLOW_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    endpoint = f"{INFERENCE_SERVER_URL}/infer/object_detection"
    payload = {
        "api_key": ROBOFLOW_API_KEY,
        "model_id": MODEL_ID,
        "image": {
            "type": "base64",
            "value": generate_valid_png_b64()
        }
    }

    print(f"Sending local Base64 inference request to {endpoint} using model '{MODEL_ID}'...")
    try:
        response = requests.post(endpoint, json=payload, timeout=30)
        if not response.ok:
            print(f"Server error ({response.status_code}): {response.text}", file=sys.stderr)
            sys.exit(1)
        result = response.json()
        predictions = result.get("predictions", [])
        print(f"Success! Inference completed (Detected {len(predictions)} object(s)).")
        for idx, pred in enumerate(predictions, 1):
            print(f"  [{idx}] Class: {pred['class']} | Confidence: {pred['confidence']:.2f}")
    except requests.exceptions.RequestException as e:
        print(f"Inference request failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_inference()
