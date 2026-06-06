from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import json
import numpy as np
import os

app = FastAPI()

# Add this to allow CORS for the validator
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.api_route("/api/latency", methods=["POST", "OPTIONS"])
async def handle_latency(request: Request):
    # Handle the CORS preflight OPTIONS request
    if request.method == "OPTIONS":
        return Response(status_code=200, headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        })
    
    # Process your logic for POST requests
    try:
        json_path = os.path.join(os.path.dirname(__file__), '..', 'q-vercel-latency.json')
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
