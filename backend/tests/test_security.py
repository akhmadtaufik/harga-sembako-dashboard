import pytest

@pytest.mark.asyncio
async def test_unauthorized_blocker(async_client):
    # Test endpoints without auth headers
    endpoints = [
        "/api/v1/analytics/anomalies?date_id=2026-06-01",
        "/api/v1/locations/provinces"
    ]
    
    for endpoint in endpoints:
        response = await async_client.get(endpoint)
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert data["data"] == []
        assert "message" in data

@pytest.mark.asyncio
async def test_holiday_weekend_edge_case(auth_client):
    # 2026-07-05 is a Sunday
    response = await auth_client.get("/api/v1/analytics/anomalies?date_id=2026-07-05")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    # Verify we get a safely handled empty array instead of 500 error
    assert data["data"] == []
