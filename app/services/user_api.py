from typing import Optional
import httpx
from app.config import API_URL
from app.services.auth_api import check_and_refresh_token

def get_profile(token: str) -> dict:
    check_and_refresh_token(token)
    with httpx.Client() as client:
        response = client.get(f"{API_URL}/user/", headers={"X-Token": token})
        return response.json()

def update_profile(token: str, payload: dict) -> dict:
    check_and_refresh_token(token)
    with httpx.Client() as client:
        response = client.put(f"{API_URL}/user", headers={"X-Token": token}, json=payload)
        return response.json()

def change_password(token: str, new_password: str) -> dict:
    check_and_refresh_token(token)
    with httpx.Client() as client:
        response = client.put(f"{API_URL}/user/password?new_password={new_password}", headers={"X-Token": token})
        return response.json()

def get_profile_by_id(token: str, user_id: str) -> dict:
    with httpx.Client() as client:
        response = client.get(f"{API_URL}/user/{user_id}", headers={"X-Token": token})
        return response.json()
