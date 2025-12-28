import requests
import json
import os
import time

API_URL = "https://logistics-agent-backend-255413983349.us-central1.run.app"

def test_health():
    print(f"Testing Health at {API_URL}/health...")
    try:
        res = requests.get(f"{API_URL}/health", timeout=10)
        print(f"Status: {res.status_code}")
        print(f"Response: {res.text}")
        return res.status_code == 200
    except Exception as e:
        print(f"FAILED: {e}")
        return False

def test_sample():
    print(f"\nTesting /sample endpoint...")
    try:
        res = requests.get(f"{API_URL}/sample", timeout=30)
        if res.status_code == 200:
            data = res.json()
            keys = list(data.keys())
            print(f"Success! Received tables: {keys}")
            # Check for data
            if "shipments" in data and len(data["shipments"]) > 0:
                print("Shipment data verified.")
                return True
        else:
            print(f"Failed with {res.status_code}: {res.text}")
    except Exception as e:
        print(f"FAILED: {e}")
    return False

def test_query():
    print(f"\nTesting /query endpoint (Agent Logic)...")
    payload = {
        "query": "Which vehicles are waiting in London?",
        "role": "Logistics Manager"
    }
    try:
        res = requests.post(f"{API_URL}/query", json=payload, timeout=45)
        if res.status_code == 200:
            data = res.json()
            print(f"Success! Response Summary: {data.get('summary')[:100]}...")
            return True
        else:
            print(f"Failed with {res.status_code}: {res.text}")
    except Exception as e:
        print(f"FAILED: {e}")
    return False

if __name__ == "__main__":
    print("--- STARTING VERIFICATION ---")
    h = test_health()
    s = test_sample()
    q = test_query()
    
    if h and s and q:
        print("\n✅ ALL CHECKS PASSED")
    else:
        print("\n❌ SOME CHECKS FAILED")
