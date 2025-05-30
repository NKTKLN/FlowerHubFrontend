from typing import Optional
import httpx
from app.config import API_URL
from app.services.auth_api import check_and_refresh_token

def get_flower_data(
    name: Optional[str] = None,
    flower_id: Optional[int] = None,
    type_id: Optional[int] = None,
    season_id: Optional[int] = None,
    usage_id: Optional[int] = None,
    seller_id: Optional[int] = None,
    country_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    limit: int = 100,
    offset: int = 0,
) -> Optional[dict]:
    params = {
        "name": name,
        "type_id": type_id,
        "flower_id": flower_id,
        "season_id": season_id,
        "usage_id": usage_id,
        "country_id": country_id,
        "min_price": min_price,
        "max_price": max_price,
        "limit": limit,
        "offset": offset,
        "seller_id": seller_id
    }
    params = {k: v for k, v in params.items() if v is not None}

    with httpx.Client() as client:
        response = client.get(f"{API_URL}/flowers/", params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching flower data: {response.status_code} - {response.text}")
            return None
