import httpx
from app.config import API_URL
from app.services.auth_api import check_and_refresh_token

def get_admin_orders(token: str) -> dict:
    check_and_refresh_token(token)
    with httpx.Client() as client:
        response = client.get(f"{API_URL}/admin/orders", headers={"X-Token": token})
    return response.json()

def admin_add_flower(token: str, payload: dict, seller_id: int) -> dict:
    check_and_refresh_token(token)
    with httpx.Client() as client:
        response = client.post(f"{API_URL}/admin/flowers?seller_id={seller_id}", json=payload, headers={"X-Token": token})
        return response.json()

def admin_add_user(token: str, payload: dict) -> dict:
    check_and_refresh_token(token)
    with httpx.Client() as client:
        response = client.post(f"{API_URL}/admin/users", json=payload, headers={"X-Token": token})
        return response.json()

def get_admin_users(token: str) -> dict:
    check_and_refresh_token(token)
    with httpx.Client() as client:
        response = client.get(f"{API_URL}/admin/users", headers={"X-Token": token})
        return response.json()

def admin_delete_user(token: str, user_id: int) -> dict:
    check_and_refresh_token(token)
    with httpx.Client() as client:
        response = client.delete(f"{API_URL}/admin/users/{user_id}", headers={"X-Token": token})
        return response.json()
