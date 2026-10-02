"""REST source client with timeout and bounded retry."""
import requests
def fetch_endpoint(base_url: str, endpoint: str, retries: int = 3) -> list[dict]:
    last = None
    for _ in range(retries):
        try:
            response = requests.get(f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}", timeout=5)
            response.raise_for_status(); payload = response.json()
            if not isinstance(payload, list): raise ValueError("source response must be a list")
            return payload
        except (requests.RequestException, ValueError) as exc: last = exc
    raise RuntimeError(f"REST ingestion failed for {endpoint}: {last}")
