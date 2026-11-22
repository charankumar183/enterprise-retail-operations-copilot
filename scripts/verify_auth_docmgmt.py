import urllib.request
import urllib.parse
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

def api_call(endpoint, method="GET", data=None, token=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())

def test_auth_and_docmgmt():
    roles = [
        ("admin", "Administrator"),
        ("manager", "Store Manager"),
        ("analyst", "Supply Chain Analyst"),
        ("planner", "Inventory Planner"),
        ("category", "Category Manager"),
        ("procurement", "Procurement Manager"),
    ]
    
    tokens = {}
    print("--- 1. TESTING ALL 6 ROLES LOGIN & JWT ---")
    for username, role_name in roles:
        status, res = api_call("/auth/json-login", method="POST", data={"username": username, "password": "admin123"})
        assert status == 200, f"Login failed for {username}"
        assert res["role"] == role_name
        assert "access_token" in res
        tokens[username] = res["access_token"]
        print(f"Role '{role_name}' ({username}): Login SUCCESS, JWT Token issued.")

    print("\n--- 2. TESTING JWT VALIDATION (/auth/me) ---")
    for username, token in tokens.items():
        status, res = api_call("/auth/me", method="GET", token=token)
        assert status == 200
        assert res["username"] == username
    print("JWT Validation on /auth/me passed for all 6 roles.")

    print("\n--- 3. TESTING BACKEND RBAC AUTHORIZATION (403 FORBIDDEN REJECTION) ---")
    # Store Manager attempts to delete a document (ID: 1) -> must be 403 Forbidden
    status, res = api_call("/documents/1", method="DELETE", token=tokens["manager"])
    print(f"Store Manager DELETE /documents/1: HTTP {status} (Expected 403) -> {res.get('detail')}")
    assert status == 403, f"Expected 403, got {status}"

    # Category Manager attempts delete -> 403 Forbidden
    status, res = api_call("/documents/1", method="DELETE", token=tokens["category"])
    print(f"Category Manager DELETE /documents/1: HTTP {status} (Expected 403)")
    assert status == 403

    print("\n--- 4. TESTING DOCUMENT REPOSITORY & VERSIONING ---")
    status, docs = api_call("/documents", method="GET", token=tokens["admin"])
    assert status == 200
    print(f"Retrieved {len(docs)} indexed enterprise documents from repository.")
    first_doc = docs[0]
    print(f"Sample Document: ID={first_doc['id']}, Filename='{first_doc['filename']}', DocType='{first_doc['doc_type']}', Version='{first_doc.get('version', 'v1.0')}', Chunks={first_doc['total_chunks']}")

    print("\nAUTHENTICATION, RBAC & DOCUMENT MANAGEMENT VERIFIED!")

if __name__ == "__main__":
    test_auth_and_docmgmt()
