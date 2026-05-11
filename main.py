from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from typing import List, Dict

app = FastAPI(title="Scope 3 Emissions Estimator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load emissions factors
df = pd.read_csv("emissions_factors.csv")
factor_dict = df.set_index("material").to_dict(orient="index")

class MaterialInput(BaseModel):
    material: str
    quantity: float
    unit: str

class EstimateRequest(BaseModel):
    materials: List[MaterialInput]

class EmissionResult(BaseModel):
    material: str
    quantity: float
    unit: str
    kg_co2e: float
    factor_used: float

@app.get("/")
def root():
    return {"message": "Scope 3 Emissions Estimator API", "available_materials": list(factor_dict.keys())}

@app.post("/estimate", response_model=Dict)
def estimate_emissions(request: EstimateRequest):
    results = []
    total_emissions = 0.0
    
    for item in request.materials:
        material = item.material.lower()
        if material not in factor_dict:
            raise HTTPException(status_code=400, detail=f"Material '{material}' not found. Available: {list(factor_dict.keys())}")
        
        factor = factor_dict[material]["kg_co2e_per_unit"]
        emissions = item.quantity * factor
        total_emissions += emissions
        
        results.append({
            "material": material,
            "quantity": item.quantity,
            "unit": item.unit,
            "kg_co2e": round(emissions, 2),
            "factor_used": factor
        })
    
    return {
        "total_kg_co2e": round(total_emissions, 2),
        "total_tons_co2e": round(total_emissions / 1000, 3),
        "breakdown": results
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)