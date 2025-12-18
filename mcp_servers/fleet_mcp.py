import pandas as pd
from fastapi import FastAPI
import os

app = FastAPI(title="Neuro-OCC Fleet MCP")

AIRCRAFT_DATA = "data/aircraft.csv"
FLIGHTS_DATA = "data/flights.csv"

def load_data(path):
    if not os.path.exists(path):
        return pd.DataFrame()
    return pd.read_csv(path)

@app.get("/aircraft")
def get_all_aircraft():
    df = load_data(AIRCRAFT_DATA)
    return df.to_dict(orient="records")

@app.get("/aircraft/{tail_number}")
def get_aircraft(tail_number: str):
    df = load_data(AIRCRAFT_DATA)
    ac = df[df['tail_number'] == tail_number]
    if ac.empty:
        return {"error": "Aircraft not found"}
    return ac.iloc[0].to_dict()

@app.get("/flights")
def get_all_flights():
    df = load_data(FLIGHTS_DATA)
    return df.to_dict(orient="records")

@app.get("/aircraft/{tail_number}/mamba-score")
def get_mamba_health_score(tail_number: str):
    # This would normally query the Mamba model
    df = load_data(AIRCRAFT_DATA)
    ac = df[df['tail_number'] == tail_number]
    if ac.empty:
        return {"error": "Aircraft not found"}
    return {"tail_number": tail_number, "health_score": float(ac.iloc[0]['health_score'])}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
