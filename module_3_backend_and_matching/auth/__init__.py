"""
Auth Package
Exports security utilities and route dependencies.
"""
from module_3_backend_and_matching.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
)
from module_3_backend_and_matching.auth.dependencies import (
    get_db,
    get_current_user,
    get_current_student
)

__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "get_db",
    "get_current_user",
    "get_current_student"
]
