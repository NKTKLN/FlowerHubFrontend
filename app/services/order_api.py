from typing import Optional
import httpx
from app.config import API_URL
from app.services.auth_api import check_and_refresh_token

def create_order(token: str, payload: dict) -> dict:
    check_and_refresh_token(token)
    cart_data = {
        "items": [
            {
                "flower_id": int(flower_id),
                "quantity": quantity
            }
            for flower_id, quantity in payload.items()
        ]
    }
    with httpx.Client() as client:
        response = client.post(f"{API_URL}/order/", headers={"X-Token": token}, json=cart_data)
        return response.json()

def get_orders(token: str) -> dict:
    check_and_refresh_token(token)
    with httpx.Client() as client:
        response = client.get(f"{API_URL}/order/orders", headers={"X-Token": token})
    return response.json()

def get_order_by_id(token: str, order_id: int) -> dict:
    check_and_refresh_token(token)
    with httpx.Client() as client:
        response = client.get(f"{API_URL}/order/orders/{order_id}", headers={"X-Token": token})
    return response.json()
