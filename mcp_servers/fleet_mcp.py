import pandas as pd
from fastapi import FastAPI, HTTPException
import os
from typing import List, Dict, Any

app = FastAPI(title="Neuro-OCC Fleet MCP")

AIRCRAFT_DATA = "data/aircraft.csv"
FLIGHTS_DATA = "data/flights.csv"

def load_data(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Data file not found: {path}")
    return pd.read_csv(path)

@app.get("/health")
async def health_check() -> Dict[str, str]:
    return {"status": "healthy", "service": "fleet_mcp"}

@app.get("/aircraft")
async def get_all_aircraft() -> List[Dict[str, Any]]:
    try:
        df = load_data(AIRCRAFT_DATA)
        return df.to_dict(orient="records")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Aircraft data not available")

@app.get("/aircraft/{tail_number}")
async def get_aircraft(tail_number: str) -> Dict[str, Any]:
    try:
        df = load_data(AIRCRAFT_DATA)
        ac = df[df['tail_number'] == tail_number]
        if ac.empty:
            raise HTTPException(status_code=404, detail="Aircraft not found")
        return ac.iloc[0].to_dict()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Aircraft data not available")

@app.get("/flights")
async def get_all_flights() -> List[Dict[str, Any]]:
    try:
        df = load_data(FLIGHTS_DATA)
        return df.to_dict(orient="records")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Flights data not available")

@app.get("/aircraft/{tail_number}/mamba-score")
async def get_mamba_health_score(tail_number: str) -> Dict[str, Any]:
    try:
        df = load_data(AIRCRAFT_DATA)
        ac = df[df['tail_number'] == tail_number]
        if ac.empty:
            raise HTTPException(status_code=404, detail="Aircraft not found")
        return {"tail_number": tail_number, "health_score": float(ac.iloc[0]['health_score'])}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Aircraft data not available")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
