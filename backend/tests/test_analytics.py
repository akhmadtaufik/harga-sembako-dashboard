import pytest
import time

@pytest.mark.asyncio
async def test_seasonality_and_spread(auth_client):
    endpoints = [
        "/api/v1/analytics/seasonality?group_id=1&year=2026",
        "/api/v1/analytics/spread/market-types?start_date=2026-06-01&end_date=2026-06-07"
    ]
    
    for endpoint in endpoints:
        response = await auth_client.get(endpoint)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)

@pytest.mark.asyncio
async def test_disparity_and_anomalies(auth_client):
    # Test National Disparity Mapping
    response = await auth_client.get("/api/v1/analytics/disparity?date_id=2026-06-01&commodity_id=1")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)

    # Test Anomalies (Max 5 records validation)
    response = await auth_client.get("/api/v1/analytics/anomalies?date_id=2026-06-01")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)
    assert len(data["data"]) <= 5, "Anomalies endpoint returned more than 5 records."

@pytest.mark.asyncio
async def test_cache_miss_vs_hit_latency(auth_client):
    # Wait to ensure no rate-limiting or pending locks interfere
    endpoint = "/api/v1/analytics/seasonality?group_id=2&year=2026"
    
    # 1. First execution (Cache Miss)
    start_time_miss = time.perf_counter()
    resp_miss = await auth_client.get(endpoint)
    end_time_miss = time.perf_counter()
    
    assert resp_miss.status_code == 200
    latency_miss_ms = (end_time_miss - start_time_miss) * 1000
    
    # 2. Second execution (Cache Hit)
    start_time_hit = time.perf_counter()
    resp_hit = await auth_client.get(endpoint)
    end_time_hit = time.perf_counter()
    
    assert resp_hit.status_code == 200
    latency_hit_ms = (end_time_hit - start_time_hit) * 1000

    # Validate cache hit intercept resolved under 50ms (AC1 requirement)
    assert latency_hit_ms < 50, f"Cache Hit latency {latency_hit_ms:.2f}ms exceeded the 50ms threshold."
    # Validate cache is indeed faster than initial request
    assert latency_hit_ms < latency_miss_ms, f"Cache Hit {latency_hit_ms:.2f}ms was not faster than Miss {latency_miss_ms:.2f}ms"
