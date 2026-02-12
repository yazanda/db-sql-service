import os
from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyHeader

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def require_api_key(api_key: str = Security(api_key_header)) -> str:
    expected = os.getenv("API_KEY", "CHANGE_ME_TO_A_LONG_RANDOM_SECRET")
    if not api_key or api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return api_key
