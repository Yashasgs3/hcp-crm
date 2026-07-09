import requests
import json

url = "http://localhost:8000/api/interactions/chat"

# Test 1: Real interaction
payload = {"message": "I met Dr. Sarah Chen today at Mercy Hospital. She's a cardiologist. We discussed our new hypertension drug CardioPlus. She was very positive and asked for samples."}
print("=== Test 1: Log Interaction ===")
print(f"POST {url}")
try:
    r = requests.post(url, json=payload, timeout=120)
    print(f"Status: {r.status_code}")
    print(f"Full response: {json.dumps(r.json(), indent=2)}")
except Exception as e:
    print(f"ERROR: {e}")
