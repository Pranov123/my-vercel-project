from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import numpy as np

app = FastAPI()

# Enable CORS for any origin so the validator can reach your endpoint
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the telemetry data bundle provided in the challenge
with open("q-vercel-latency.json", "r") as f:
    data = json.load(f)

@app.post("/api/latency")
async def get_latency(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 180)
    
    results = {}
    
    for region in regions:
        # Filter telemetry data for this specific region
        region_data = [item for item in data if item["region"] == region]
        if not region_data:
            continue
            
        latencies = [item["latency_ms"] for item in region_data]
        uptimes = [item["uptime_pct"] for item in region_data]
        
        # Calculate the required metrics
        results[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": len([l for l in latencies if l > threshold])
        }
        
    return results
