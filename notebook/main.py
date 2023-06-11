from fastapi import FastAPI
from pydantic import BaseModel
import pickle
import pandas as pd
import numpy as np
import uvicorn
import os

# call the app
app = FastAPI(title="API")

# Endpoints
@app.get("/")
def root():
    return {"API": "This is an API for sepsis prediction."}


# Load the model and scaler
def load_model_and_scaler():
    with open("model.pkl", "rb") as f1, open("scaler.pkl", "rb") as f2:
        return pickle.load(f1), pickle.load(f2)

model, scaler = load_model_and_scaler()

def predict(df, endpoint="simple"):
    # Scaling
    scaled_df = scaler.transform(df)

    # Prediction
    prediction = model.predict_proba(scaled_df)

    highest_proba = prediction.argmax(axis=1)

    predicted_labels = ["Patient doesn't have sepsis" if i == 0 else "Patient has sepsis" for i in highest_proba]
    print(f"Predicted labels: {predicted_labels}")

    response = []
    for label in predicted_labels:
        output = {
            "predicted_label": label
        }
        response.append(output)

    return response


class Patient(BaseModel):
    Blood_Work_R1: int
    Blood_Pressure: int
    Blood_Work_R3: int
    BMI: float
    Blood_Work_R4: float
    Patient_age: int

## Prediction endpoint
@app.post("/predict")
def predict_sepsis(patient: Patient):
    # Make prediction
    data = pd.DataFrame(patient.dict(), index=[0])
    parsed = predict(df=data)
    return {"output": parsed}

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)