import json
import urllib.request

def verify_live_api():
    base_url = "http://127.0.0.1:8000"
    
    # 1. Health
    with urllib.request.urlopen(f"{base_url}/health", timeout=5) as resp:
        health_data = json.loads(resp.read().decode())
        print(f"Health Check: HTTP {resp.status} - {health_data}")
        assert resp.status == 200
        assert health_data["status"] == "healthy"

    # 2. Swagger /docs
    with urllib.request.urlopen(f"{base_url}/docs", timeout=5) as resp:
        print(f"Swagger UI (/docs): HTTP {resp.status}")
        assert resp.status == 200

    # 3. OpenAPI Schema
    with urllib.request.urlopen(f"{base_url}/openapi.json", timeout=5) as resp:
        openapi = json.loads(resp.read().decode())
        paths = list(openapi.get("paths", {}).keys())
        print(f"OpenAPI Schema: HTTP {resp.status} - {len(paths)} endpoints registered:")
        for p in paths:
            methods = list(openapi["paths"][p].keys())
            print(f"  [{', '.join(methods).upper()}] {p}")

    print("\nALL LIVE API GATEWAY & SWAGGER VERIFICATIONS PASSED!")

if __name__ == "__main__":
    verify_live_api()
