from typing import cast, Any, Dict, Optional
from fastapi.testclient import TestClient


BASE_URL = "/api/v1"


def send_get_request(client: TestClient, relative_url: str) -> Dict:
    response = client.get(f"{BASE_URL}/{relative_url}")
    assert 300 > response.status_code >= 200
    return cast(Dict, response.json())


def send_post_request(
    client: TestClient, relative_url: str, json: Optional[Any] = None
) -> Dict:
    response = client.post(f"{BASE_URL}/{relative_url}", json=json)
    assert 300 > response.status_code >= 200
    return cast(Dict, response.json())
