from typing import Optional
import httpx
from nicegui import app, ui
from app.config import API_URL

def login(email: str, password: str) -> Optional[dict]:
    with httpx.Client() as client:
        response = client.post(f"{API_URL}/auth/login", json={"email": email, "password": password})
        return response.json()

def register(email: str, password: str, first_name: str, last_name: str, is_user_seller: bool) -> Optional[dict]:
    with httpx.Client() as client:
        response = client.post(f"{API_URL}/auth/register", json={
            "email": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
            "is_user_seller": is_user_seller
        })
        return response.json()

def refresh_token(token: str) -> Optional[dict]:
    with httpx.Client() as client:
        response = client.post(f"{API_URL}/auth/refresh", json={"refresh_token": token})
        return response.json()

def check_token(token: str) -> bool:
    with httpx.Client() as client:
        response = client.post(f"{API_URL}/auth/check-token", headers={"X-Token": token})
        return response.json().get("detail") == "Токен активен"

def check_and_refresh_token(access_token: str):
    if check_token(access_token):
        return

    tokens = refresh_token(app.storage.user.get('refresh_token'))
    if tokens.get('access_token', None) is None:
        ui.navigate.to('/login')
        return

    app.storage.user['auth_token'] = tokens['access_token']
    app.storage.user['refresh_token'] = tokens['refresh_token']
