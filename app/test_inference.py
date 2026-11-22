import os
import sys
import requests

# Get API Key from environment variables securely, never hardcode
ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY")
INFERENCE_SERVER_URL = os.getenv("INFERENCE_SERVER_URL", "http://localhost:9001")
# Use Roboflow public model example (e.g., hard hat detection model)
MODEL_ID = os.getenv("ROBOFLOW_MODEL_ID", "hard-hat-sample-txe1v/1")

def run_inference(image_url: str):
    if not ROBOFLOW_API_KEY:
        print("Error: ROBOFLOW_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    endpoint = f"{INFERENCE_SERVER_URL}/{MODEL_ID}"
    params = {
        "api_key": ROBOFLOW_API_KEY,
        "image": image_url
    }

    print(f"Sending inference request to {endpoint}...")
    try:
        response = requests.post(endpoint, params=params, timeout=10)
        response.raise_for_status()
        result = response.json()
        predictions = result.get("predictions", [])
        print(f"Success! Detected {len(predictions)} object(s).")
        for idx, pred in enumerate(predictions, 1):
            print(f"  [{idx}] Class: {pred['class']} | Confidence: {pred['confidence']:.2f}")
    except requests.exceptions.RequestException as e:
        print(f"Inference request failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    # Test with a public image URL
    sample_image = "https://roboflow.com"
    run_inference(sample_image)
