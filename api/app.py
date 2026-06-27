from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
import joblib
import numpy as np

BASE = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE / "ml" / "models" / "f1_winner_model.pkl"


app = FastAPI(
    title="F1 Winner Prediction API",
    version="1.0.0",
    description="Predicts whether a driver will win a race based on race and driver features."
)

# Load model at startup
model = joblib.load(MODEL_PATH)

class PredictionRequest(BaseModel):
    season: int
    round: int
    grid_position: int
    circuit_id: str
    points: float
    driver_nationality: str
    constructor_nationality: str

class PredictionResponse(BaseModel):
    winner: bool
    probability: float

# Simple encoders (must match training logic)
# For now, we use hash-based encoding to stay stateless.
def encode_str(value: str) -> int:
    return abs(hash(value)) % (10_000)

@app.post("/predict_winner", response_model=PredictionResponse)
def predict_winner(req: PredictionRequest):
    # Encode categorical features (must mirror training approach)
    circuit_enc = encode_str(req.circuit_id)
    driver_nat_enc = encode_str(req.driver_nationality)
    constructor_nat_enc = encode_str(req.constructor_nationality)

    features = np.array([[
        req.grid_position,
        req.season,
        req.round,
        req.points,
        circuit_enc,
        driver_nat_enc,
        constructor_nat_enc
    ]])

    proba = model.predict_proba(features)[0][1]
    winner = bool(proba >= 0.5)

    return PredictionResponse(
        winner=winner,
        probability=float(proba)
    )
