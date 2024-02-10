import json
import pytest
from fastapi.testclient import TestClient
from production_plan.api import app

client = TestClient(app)

def test_post_productionplan():
    with open("example_payloads/payload3.json") as f:
        request = json.load(f)
    
    with open("example_payloads/response3.json") as f:
        expected_response = json.load(f)
    
    response = client.post(
        "/productionplan",
        json=request
    )
    assert response.status_code == 200
    assert response.json() == expected_response