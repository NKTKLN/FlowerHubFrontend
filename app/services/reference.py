import httpx
from app.config import API_URL
from app.services.auth_api import check_and_refresh_token

class ReferenceAPI:
    def get_types(self) -> dict:
        with httpx.Client() as client:
            response = client.get(f"{API_URL}/flowers/types")
            return response.json()

    def get_usages(self) -> dict:
        with httpx.Client() as client:
            response = client.get(f"{API_URL}/flowers/usages")
        return response.json()

    def get_seasons(self) -> dict:
        with httpx.Client() as client:
            response = client.get(f"{API_URL}/flowers/seasons")
        return response.json()
    
    def get_countries(self) -> dict:
        with httpx.Client() as client:
            response = client.get(f"{API_URL}/flowers/countries")
        return response.json()

    def add_type(self, token: str, payload: dict) -> dict:
        check_and_refresh_token(token)
        with httpx.Client() as client:
            response = client.post(f"{API_URL}/flowers/types", json=payload, headers={"X-Token": token})
        return response.json()
    
    def add_usage(self, token: str, payload: dict) -> dict:
        check_and_refresh_token(token)
        with httpx.Client() as client:
            response = client.post(f"{API_URL}/flowers/usages", json=payload, headers={"X-Token": token})
        return response.json()
    
    def add_season(self, token: str, payload: dict) -> dict:
        check_and_refresh_token(token)
        with httpx.Client() as client:
            response = client.post(f"{API_URL}/flowers/seasons", json=payload, headers={"X-Token": token})
        return response.json()
    
    def add_country(self, token: str, payload: dict) -> dict:
        check_and_refresh_token(token)
        with httpx.Client() as client:
            response = client.post(f"{API_URL}/flowers/countries", json=payload, headers={"X-Token": token})
        return response.json()

    def delete_type(self, token: str, type_id: int) -> dict:
        check_and_refresh_token(token)
        with httpx.Client() as client:
            response = client.delete(f"{API_URL}/flowers/types/{type_id}", headers={"X-Token": token})
        return response.json()
    
    def delete_usage(self, token: str, usage_id: int) -> dict:
        check_and_refresh_token(token)
        with httpx.Client() as client:
            response = client.delete(f"{API_URL}/flowers/usages/{usage_id}", headers={"X-Token": token})
        return response.json()
    
    def delete_season(self, token: str, season_id: int) -> dict:
        check_and_refresh_token(token)
        with httpx.Client() as client:
            response = client.delete(f"{API_URL}/flowers/seasons/{season_id}", headers={"X-Token": token})
        return response.json()
    
    def delete_country(self, token: str, country_id: int) -> dict:
        check_and_refresh_token(token)
        with httpx.Client() as client:
            response = client.delete(f"{API_URL}/flowers/countries/{country_id}", headers={"X-Token": token})
        return response.json()

# Initialize the ReferenceAPI instance
reference = ReferenceAPI()
