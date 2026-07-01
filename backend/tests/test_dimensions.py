import pytest
import time

@pytest.mark.asyncio
async def test_location_and_commodity_evaluation(auth_client):
    endpoints = [
        "/api/v1/locations/provinces",
        "/api/v1/locations/regencies?province_id=11",
        "/api/v1/commodities/groups",
        "/api/v1/markets"
    ]
    
    for endpoint in endpoints:
        start_time = time.perf_counter()
        response = await auth_client.get(endpoint)
        end_time = time.perf_counter()
        
        # Verify 200 OK
        assert response.status_code == 200
        
        # Verify latency < 200ms
        latency_ms = (end_time - start_time) * 1000
        assert latency_ms < 200, f"Endpoint {endpoint} exceeded 200ms latency ({latency_ms:.2f}ms)"
        
        # Verify GenericResponseModel schema wrapper
        data = response.json()
        assert "success" in data
        assert data["success"] is True
        assert "data" in data
        assert isinstance(data["data"], list)

@pytest.mark.asyncio
async def test_geospatial_coalesce_check(auth_client):
    response = await auth_client.get("/api/v1/markets")
    assert response.status_code == 200
    data = response.json()["data"]
    
    # Check that every single market record has valid coordinates
    for market in data:
        assert "latitude" in market and market["latitude"] is not None
        assert "longitude" in market and market["longitude"] is not None
