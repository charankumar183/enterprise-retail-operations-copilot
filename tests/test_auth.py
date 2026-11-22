import pytest
from datetime import timedelta
from backend.app.services.auth_service import verify_password, get_password_hash, create_access_token
from jose import jwt
from backend.app.config import settings

def test_password_hashing():
    pwd = "EnterprisePassword2026!"
    hashed = get_password_hash(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

def test_create_and_decode_jwt():
    data = {"sub": "analyst", "role": "Supply Chain Analyst", "id": 3}
    token = create_access_token(data, expires_delta=timedelta(minutes=30))
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == "analyst"
    assert payload["role"] == "Supply Chain Analyst"
    assert payload["id"] == 3
