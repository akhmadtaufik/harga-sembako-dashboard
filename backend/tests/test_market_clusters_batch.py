import asyncio
import httpx
import time
from typing import List, Dict, Any

BASE_URL = "http://localhost:8000/api/v1"

async def fetch_json(client: httpx.AsyncClient, url: str) -> Dict[str, Any]:
    response = await client.get(url, timeout=10.0)
    response.raise_for_status()
    return response.json()

async def validate_cluster(
    client: httpx.AsyncClient, 
    semaphore: asyncio.Semaphore, 
    commodity: Dict[str, Any], 
    regency: Dict[str, Any], 
    results: Dict[str, List[Dict[str, Any]]]
):
    url = f"{BASE_URL}/analytics/market-clusters?commodity_id={commodity['commodity_id']}&regency_id={regency['regency_id']}"
    async with semaphore:
        try:
            response = await client.get(url, timeout=30.0)
            
            if response.status_code != 200:
                results["failed"].append({
                    "commodity": commodity,
                    "regency": regency,
                    "error": f"HTTP {response.status_code}"
                })
                return

            data_res = response.json()
            items = data_res.get("data", [])
            
            if not items:
                results["fallback"].append({
                    "commodity": commodity,
                    "regency": regency,
                    "reason": "Empty dataset",
                    "markets_count": 0
                })
                return
                
            labels = set(item.get("cluster_label") for item in items)
            
            if len(labels) <= 1:
                results["fallback"].append({
                    "commodity": commodity,
                    "regency": regency,
                    "reason": f"All assigned to single label: {list(labels)[0]}",
                    "markets_count": len(items)
                })
            else:
                results["success"].append({
                    "commodity": commodity,
                    "regency": regency,
                    "markets_count": len(items),
                    "clusters": list(labels)
                })
                
        except Exception as e:
            results["failed"].append({
                "commodity": commodity,
                "regency": regency,
                "error": str(e)
            })

async def main():
    print("Starting Async Batch Validation for Market Clusters...")
    start_time = time.perf_counter()
    
    headers = {
        "X-API-Key": "i9dnLnpW9PS2EJ8ADQBU955vE"
    }
    
    async with httpx.AsyncClient(headers=headers) as client:
        print("Fetching static dimensions...")
        try:
            com_res = await fetch_json(client, f"{BASE_URL}/commodities/items")
            commodities = com_res.get("data", [])
            
            reg_res = await fetch_json(client, f"{BASE_URL}/locations/regencies")
            regencies = reg_res.get("data", [])
            
        except Exception as e:
            print(f"Failed to fetch static dimensions: {e}")
            return
            
        print(f"Found {len(commodities)} commodities and {len(regencies)} regencies.")
        
        combinations = []
        for c in commodities:
            for r in regencies:
                combinations.append((c, r))
                
        total_combos = len(combinations)
        print(f"Total Combinations to test: {total_combos}")
        
        results = {
            "success": [],
            "fallback": [],
            "failed": []
        }
        
        semaphore = asyncio.Semaphore(50)  # Max 50 concurrent requests
        
        print("Running batch validation...")
        tasks = [
            validate_cluster(client, semaphore, c, r, results) 
            for c, r in combinations
        ]
        
        # We can use asyncio.gather for this
        await asyncio.gather(*tasks)
        
    end_time = time.perf_counter()
    duration = end_time - start_time
    
    print("\n" + "="*50)
    print(" BATCH VALIDATION SUMMARY REPORT ")
    print("="*50)
    print(f"Total Time Taken     : {duration:.2f} seconds")
    print(f"Total Tested         : {total_combos}")
    print(f"Success (Clustered)  : {len(results['success'])}")
    print(f"Fallback (Insufficient) : {len(results['fallback'])}")
    print(f"Failed               : {len(results['failed'])}")
    print("="*50)
    
    if results['failed']:
        print("\n--- SAMPLE ERRORS ---")
        for i, f in enumerate(results['failed'][:5]):
            print(f"{i+1}. [{f['regency']['name']}] - [{f['commodity']['name']}] | Error: {f['error']}")

    if results['success']:
        print("\n--- TOP 10 SUCCESS HIGHLIGHTS ---")
        # Sort by markets count descending to see the most robust clusterings first
        sorted_success = sorted(results['success'], key=lambda x: x['markets_count'], reverse=True)
        for i, s in enumerate(sorted_success[:10]):
            r_name = s['regency']['name']
            c_name = s['commodity']['name']
            count = s['markets_count']
            clusters = ", ".join(s['clusters'])
            print(f"{i+1}. [{r_name}] - [{c_name}] | Total Markets: {count} | Clusters Formed: [{clusters}]")

if __name__ == "__main__":
    asyncio.run(main())
