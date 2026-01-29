import pytest
from fastapi import status

@pytest.fixture
def auth_header(client):
    email = "qruser@example.com"
    password = "password123"
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password}
    )
    response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_create_qr_code(client, auth_header):
    response = client.post(
        "/api/v1/qr-codes/",
        json={"url": "https://example.com", "color": "#FF0000", "size": 300},
        headers=auth_header
    )
    assert response.status_code == status.HTTP_201_CREATED, f"Failed to create QR: {response.text}"
    assert response.headers["content-type"] == "image/png"
    assert "X-QR-UUID" in response.headers

def test_list_qr_codes(client, auth_header):
    # Create one first
    res = client.post(
        "/api/v1/qr-codes/",
        json={"url": "https://example1.com", "color": "#000000", "size": 300},
        headers=auth_header
    )
    assert res.status_code == status.HTTP_201_CREATED, f"Failed to create QR: {res.text}"
    
    response = client.get("/api/v1/qr-codes/", headers=auth_header)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1, f"Expected at least 1 QR code, got {data}"
    assert data[0]["url"] == "https://example1.com"

def test_get_qr_stats_unauthorized(client):
    response = client.get("/api/v1/qr-codes/some-uuid/stats")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_scan_qr_flow(client, auth_header):
    # 1. Create QR
    create_res = client.post(
        "/api/v1/qr-codes/",
        json={"url": "https://google.com", "color": "#FF00FF", "size": 400},
        headers=auth_header
    )
    assert create_res.status_code == status.HTTP_201_CREATED, f"Failed to create QR: {create_res.text}"
    qr_uuid = create_res.headers["X-QR-UUID"]
    
    # 2. Scan (GET /scan/{uuid})
    # allow_redirects=False as we want to check the 307
    scan_res = client.get(f"/api/v1/scan/{qr_uuid}", follow_redirects=False)
    assert scan_res.status_code == 307
    assert scan_res.headers["location"] == "https://google.com"
    
    # 3. Check stats
    stats_res = client.get(f"/api/v1/qr-codes/{qr_uuid}/stats", headers=auth_header)
    assert stats_res.status_code == 200
    stats_data = stats_res.json()
    assert stats_data["total_scans"] == 1
    assert len(stats_data["scans"]) == 1
