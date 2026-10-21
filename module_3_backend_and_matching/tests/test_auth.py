"""
Unit Tests for Authentication and Security
Tests password hashing with bcrypt, JWT token issuing, expiry, and payload validation.
"""
from datetime import timedelta
import pytest
import jwt

from module_3_backend_and_matching.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
)
from module_3_backend_and_matching.config import settings


def test_password_hashing_and_verification():
    raw_password = "SecureStudentPassword@123"
    hashed = hash_password(raw_password)

    assert hashed != raw_password
    assert hashed.startswith("$2b$")  # Standard bcrypt header
    assert verify_password(raw_password, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False


def test_jwt_access_token_creation_and_decoding():
    user_payload = {
        "sub": "user-uuid-1234",
        "email": "student@college.edu",
        "role": "student"
    }
    token = create_access_token(user_payload)
    assert isinstance(token, str)

    decoded = decode_token(token)
    assert decoded["sub"] == "user-uuid-1234"
    assert decoded["email"] == "student@college.edu"
    assert decoded["role"] == "student"
    assert decoded["type"] == "access"
    assert "exp" in decoded


def test_jwt_refresh_token_type():
    token_data = {"sub": "user-uuid-5678", "role": "student"}
    refresh_token = create_refresh_token(token_data)
    decoded = decode_token(refresh_token)

    assert decoded["sub"] == "user-uuid-5678"
    assert decoded["type"] == "refresh"


def test_expired_token_handling():
    user_payload = {"sub": "user-uuid-9999"}
    # Token expired 10 minutes ago
    expired_token = create_access_token(user_payload, expires_delta=timedelta(minutes=-10))

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_token(expired_token)
