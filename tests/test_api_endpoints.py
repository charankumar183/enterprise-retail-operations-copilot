import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Enterprise AI Retail Operations" in data["service"]

def test_json_login():
    response = client.post(
        "/api/v1/auth/json-login",
        json={"username": "manager", "password": "admin123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "Store Manager"

def test_products_list():
    response = client.get("/api/v1/products")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 5
    product_ids = [p["product_id"] for p in data]
    assert "P100" in product_ids or "PRODUCT-X" in product_ids

def test_inventory_overview():
    response = client.get("/api/v1/inventory/overview")
    assert response.status_code == 200
    data = response.json()
    assert data["total_products"] >= 5
    assert len(data["inventory_items"]) >= 5

def test_chat_rag_endpoint():
    response = client.post(
        "/api/v1/chat",
        json={"query": "What are the standard receiving procedures for warehouse operations?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["detected_intent"] == "RAG Search"
    assert len(data["citations"]) > 0
    assert "Receiving" in data["response"] or "freight" in data["response"].lower()

def test_chat_sql_endpoint():
    response = client.post(
        "/api/v1/chat",
        json={"query": "Which vendor supplies Product ABC?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["detected_intent"] == "SQL Analytics"
    assert "Verdant" in data["response"] or "SUP-ABC" in data["response"]

def test_report_generation_endpoint():
    response = client.post(
        "/api/v1/reports/generate",
        json={"report_type": "daily_store_ops", "target_id": "STORE-105"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "Daily Operations Report" in data["title"]
    assert "gross_sales" in data["key_metrics"]

def test_evaluation_benchmark_endpoint():
    response = client.get("/api/v1/evaluation/benchmark")
    assert response.status_code == 200
    data = response.json()
    assert len(data["models"]) >= 2
    assert data["benchmark_dataset_size"] > 0

def test_rbac_enforcement_on_document_delete():
    # Login as Store Manager (manager)
    mgr_res = client.post("/api/v1/auth/json-login", json={"username": "manager", "password": "admin123"})
    mgr_token = mgr_res.json()["access_token"]
    
    # Attempt delete with Store Manager token -> MUST return 403 Forbidden
    del_res = client.delete("/api/v1/documents/1", headers={"Authorization": f"Bearer {mgr_token}"})
    assert del_res.status_code == 403
    assert "Operation not permitted" in del_res.json()["detail"]

    # Login as Administrator (admin)
    admin_res = client.post("/api/v1/auth/json-login", json={"username": "admin", "password": "admin123"})
    admin_token = admin_res.json()["access_token"]
    assert admin_token is not None
