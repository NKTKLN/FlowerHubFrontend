import httpx
from app.config import API_URL
from app.services.auth_api import check_and_refresh_token

def seller_add_flower(token: str, payload: dict) -> dict:
    check_and_refresh_token(token)
    with httpx.Client() as client:
        response = client.post(f"{API_URL}/seller/flowers", json=payload, headers={"X-Token": token})
        return response.json()

def seller_edit_flower(token: str, flower_id: int, payload: dict) -> dict:
    check_and_refresh_token(token)
    with httpx.Client() as client:
        response = client.put(f"{API_URL}/seller/flowers/{flower_id}", json=payload, headers={"X-Token": token})
        return response.json()

def delete_flower(token: str, flower_id: int):
    check_and_refresh_token(token)
    with httpx.Client() as client:
        response = client.delete(f"{API_URL}/seller/flowers/{flower_id}", headers={"X-Token": token})
    return response.json()

def get_seller_orders(token: str) -> dict:
    check_and_refresh_token(token)
    with httpx.Client() as client:
        response = client.get(f"{API_URL}/seller/orders", headers={"X-Token": token})
    return response.json()

def update_order_status(token: str, order_id: int) -> dict:
    check_and_refresh_token(token)
    with httpx.Client() as client:
        response = client.get(f"{API_URL}/seller/change_order_status/{order_id}", headers={"X-Token": token})
    return response.json()
