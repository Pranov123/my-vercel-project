from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import numpy as np
import os

app = FastAPI()

# This is the "secret sauce" to fix the "Failed to fetch" error
# It allows the validator's domain to talk to your API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/latency")
async def get_latency(request: Request):
    try:
        # Looking for the JSON file in the root directory
        json_path = os.path.join(os.path.dirname(__file__), '..', 'q-vercel-latency.json')
        
        with open(json_path, "r") as f:
            data = json.load(f)
        
        body = await request.json()
        regions = body.get("regions", [])
        threshold = body.get("threshold_ms", 180)
        
        results = {}
        for region in regions:
            # Filter data for the requested region
            region_data = [item for item in data if item["region"] == region]
            if not region_data: 
                continue
            
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

# Optional: Keep this to prevent the root 404 if you want
@app.get("/api/latency")
async def ping():
    return {"message": "API is online. Please send a POST request."}
