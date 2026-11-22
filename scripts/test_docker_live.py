import urllib.request
import json

def test_docker_pipeline():
    print("--- TESTING DOCKER + NGINX END-TO-END VIA PORT 80 ---")
    queries = [
        "What are the standard receiving procedures for warehouse operations?",
        "Which vendor supplies Product ABC?",
        "Why is Product P100 frequently going out of stock?",
        "Generate a replenishment checklist for Store 210.",
        "Generate a daily operations report for Store 105."
    ]
    
    for q in queries:
        req = urllib.request.Request(
            "http://localhost/api/v1/chat",
            data=json.dumps({"query": q}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())
            intent = data["detected_intent"]
            route = data["route_taken"]
            cits = len(data["citations"])
            latency = data.get("response_latency_ms", 0.0)
            retrieval_ms = data.get("retrieval_time_ms", 0.0)
            preview = data["response"][:80].replace("\n", " ")
            print(f"Query: '{q}'")
            print(f"  Route: {route} | Citations: {cits} | Latency: {latency:.2f} ms (Retrieval: {retrieval_ms:.2f} ms)")
            print(f"  Response: {preview}...\n")

if __name__ == "__main__":
    test_docker_pipeline()
