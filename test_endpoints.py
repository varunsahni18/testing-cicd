import os
import time
import requests
import pytest
from fastapi.testclient import TestClient
from main import app

# If BASE_URL is set, we use integration tests via HTTP; otherwise, we use TestClient.
def get_client():
    base_url = os.getenv("BASE_URL")
    if base_url:
        # Integration mode: return the base URL to be used with requests.
        # Wait until the container is ready.
        wait_for_container(base_url)
        return None  # We won't use TestClient in this mode.
    else:
        # Local testing mode: return a TestClient instance.
        return TestClient(app)

def wait_for_container(base_url, timeout=60, interval=2):
    """Wait until the /add endpoint returns a valid response or timeout is reached."""
    url = f"{base_url}/add?a=1&b=2"  # a quick test endpoint
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.post(url)
            if response.status_code == 200:
                return
        except Exception:
            pass
        time.sleep(interval)
    pytest.fail("Docker container did not become ready in time.")

def call_add_endpoint(client):
    payload = {"a": 10, "b": 20}
    base_url = os.getenv("BASE_URL")
    if base_url:
        # Integration mode using requests.
        response = requests.post(f"{base_url}/add", params=payload)
    else:
        # Local mode using TestClient.
        response = client.post("/add", params=payload)
    return response

def test_add_numbers():
    client = get_client()
    response = call_add_endpoint(client)
    # Check that we get a 200 OK response.
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    # Check that the response json is as expected.
    assert response.json() == {"sum": 30}, f"Unexpected result: {response.json()}"
