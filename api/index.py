from fastapi import FastAPI, Request
import json
import numpy as np
import os

app = FastAPI()
# Add this above your existing @app.post("/api/latency") block
@app.get("/api/latency")
async def test_get():
    return {"message": "The API is alive! Now send a POST request to test the logic."}
@app.post("/api/latency")
async def get_latency(request: Request):
    try:
        # Check if file exists in the current directory
        json_path = os.path.join(os.path.dirname(__file__), 'q-vercel-latency.json')
        with open(json_path, "r") as f:
            data = json.load(f)
        
        body = await request.json()
        regions = body.get("regions", [])
        threshold = body.get("threshold_ms", 180)
        
        results = {}
        for region in regions:
            region_data = [item for item in data if item["region"] == region]
            if not region_data: continue
            
            latencies = [item["latency_ms"] for item in region_data]
            uptimes = [item["uptime_pct"] for item in region_data]
            
            results[region] = {
                "avg_latency": float(np.mean(latencies)),
                "p95_latency": float(np.percentile(latencies, 95)),
                "avg_uptime": float(np.mean(uptimes)),
                "breaches": len([l for l in latencies if l > threshold])
            }
        return results
    except Exception as e:
        return {"error": str(e)}
