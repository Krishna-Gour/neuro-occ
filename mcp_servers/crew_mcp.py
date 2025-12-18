import pandas as pd
from fastapi import FastAPI
from typing import List, Optional
import os

app = FastAPI(title="Neuro-OCC Crew MCP")

DATA_PATH = "data/pilots.csv"

def load_pilots():
    if not os.path.exists(DATA_PATH):
        return pd.DataFrame()
    return pd.read_csv(DATA_PATH)

@app.get("/pilots")
def get_pilots():
    df = load_pilots()
    return df.to_dict(orient="records")

@app.get("/pilots/{pilot_id}")
def get_pilot(pilot_id: str):
    df = load_pilots()
    pilot = df[df['pilot_id'] == pilot_id]
    if pilot.empty:
        return {"error": "Pilot not found"}
    return pilot.iloc[0].to_dict()

@app.get("/pilots/status/fatigue")
def get_high_fatigue_pilots(threshold: float = 0.3):
    df = load_pilots()
    high_fatigue = df[df['fatigue_score'] > threshold]
    return high_fatigue.to_dict(orient="records")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
