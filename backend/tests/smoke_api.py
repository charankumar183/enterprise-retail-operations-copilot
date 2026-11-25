"""API smoke check: isolated SQLite test storage; production Docker uses PostgreSQL."""
import os

os.environ['DATABASE_URL'] = 'sqlite+pysqlite:///' + os.path.join(
    os.environ['TEMP'], 'retail_operations_smoke.db'
).replace('\\', '/')

os.environ['AUTO_INDEX_SAMPLES'] = 'false'
os.environ['JWT_SECRET'] = 'testing_test_jwt_secret_123456'

from fastapi.testclient import TestClient
from app.main import app

with TestClient(app) as client:
    assert client.get('/health').status_code == 200

    res = client.post(
        '/api/auth/login',
        json={'email': 'admin@demo.retail', 'password': 'RetailDemo2026!'}
    )
    print('login', res.status_code, res.json() if res.status_code != 200 else 'ok')
    assert res.status_code == 200

    h = {'Authorization': 'Bearer ' + res.json()['access_token']}

    for u in [
        '/api/dashboard',
        '/api/products?q=P100',
        '/api/inventory?q=P100',
        '/api/documents',
        '/api/admin/users'
    ]:
        resp = client.get(u, headers=h)
        print(u, resp.status_code)
        assert resp.status_code == 200

    resp = client.post(
        '/api/chat',
        json={'question': 'Show inventory for Product P100 across warehouses'},
        headers=h
    )
    print('chat', resp.status_code, resp.json().get('intent'), resp.json().get('mode'))
    assert resp.status_code == 200 and resp.json()['intent'] == 'sql'

    assert client.get('/api/admin/users').status_code in (403, 401)

    print('SMOKE PASSED')