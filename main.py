# final_api.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from typing import List, Dict, Any

app = FastAPI(
    title="EPA GHG Emissions Estimator",
    description="Real EPA data from GHG Emission Factors Hub 2025",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the real EPA data
df = pd.read_csv("all_epa_factors.csv")

# Create lookup dictionary
FACTOR_DICT = {}
for _, row in df.iterrows():
    material = row['material']
    FACTOR_DICT[material] = {
        "factor": row['factor'],
        "unit": row['unit'],
        "display_name": row['display_name'],
        "table": int(row['table']),
        "category": row['category']
    }

class MaterialInput(BaseModel):
    material: str
    quantity: float

class EstimateRequest(BaseModel):
    materials: List[MaterialInput]

@app.get("/")
def root():
    """Get available materials and API info"""
    return {
        "message": "EPA GHG Emissions Estimator",
        "data_source": "EPA GHG Emission Factors Hub 2025",
        "last_modified": "January 15, 2025",
        "total_factors": len(FACTOR_DICT),
        "available_categories": df['category'].unique().tolist(),
        "sample_materials": list(FACTOR_DICT.keys())[:20],
        "note": "These are industry averages. Actual emissions vary by specific supplier/producer."
    }

@app.get("/materials")
def list_materials(category: str = None):
    """List all available materials, optionally filtered by category"""
    if category:
        filtered = df[df['category'] == category]
        return {
            "category": category,
            "materials": filtered['display_name'].tolist()
        }
    else:
        return {
            "total": len(FACTOR_DICT),
            "materials_by_category": {
                category: df[df['category'] == category]['display_name'].tolist()
                for category in df['category'].unique()
            }
        }

@app.get("/categories")
def list_categories():
    """List all available categories"""
    return {
        "categories": df['category'].unique().tolist()
    }

@app.get("/factor/{material}")
def get_factor(material: str):
    """Get emission factor for a specific material"""
    material_key = material.lower().replace(' ', '_').replace('(', '').replace(')', '')
    
    if material_key not in FACTOR_DICT:
        raise HTTPException(404, f"Material '{material}' not found")
    
    factor_data = FACTOR_DICT[material_key]
    return {
        "material": factor_data['display_name'],
        "factor": factor_data['factor'],
        "unit": factor_data['unit'],
        "category": factor_data['category'],
        "source": f"EPA Table {factor_data['table']}",
        "note": "Industry average. Actual emissions may vary."
    }

@app.post("/estimate")
def estimate_emissions(request: EstimateRequest):
    """Calculate emissions based on material quantities"""
    results = []
    total_kg = 0.0
    
    for item in request.materials:
        material_key = item.material.lower().replace(' ', '_').replace('(', '').replace(')', '')
        
        if material_key not in FACTOR_DICT:
            raise HTTPException(404, f"Material '{item.material}' not found")
        
        factor_data = FACTOR_DICT[material_key]
        emissions_kg = item.quantity * factor_data['factor']
        total_kg += emissions_kg
        
        results.append({
            "material": factor_data['display_name'],
            "quantity": item.quantity,
            "unit": factor_data['unit'],
            "kg_co2e": round(emissions_kg, 2),
            "factor_used": factor_data['factor'],
            "category": factor_data['category'],
            "source": f"EPA Table {factor_data['table']}"
        })
    
    return {
        "total_kg_co2e": round(total_kg, 2),
        "total_tons_co2e": round(total_kg / 1000, 3),
        "total_lbs_co2e": round(total_kg * 2.20462, 2),
        "data_source": "EPA GHG Emission Factors Hub 2025",
        "disclaimer": "These are industry average estimates. For actual emissions, use supplier-specific data.",
        "breakdown": results
    }

@app.get("/compare")
def compare_materials(material1: str, quantity1: float, material2: str, quantity2: float):
    """Compare emissions between two materials"""
    m1_key = material1.lower().replace(' ', '_').replace('(', '').replace(')', '')
    m2_key = material2.lower().replace(' ', '_').replace('(', '').replace(')', '')
    
    if m1_key not in FACTOR_DICT:
        raise HTTPException(404, f"Material '{material1}' not found")
    if m2_key not in FACTOR_DICT:
        raise HTTPException(404, f"Material '{material2}' not found")
    
    m1 = FACTOR_DICT[m1_key]
    m2 = FACTOR_DICT[m2_key]
    
    em1 = quantity1 * m1['factor']
    em2 = quantity2 * m2['factor']
    
    return {
        "material_1": {
            "name": m1['display_name'],
            "quantity": quantity1,
            "unit": m1['unit'],
            "total_kg_co2e": round(em1, 2)
        },
        "material_2": {
            "name": m2['display_name'],
            "quantity": quantity2,
            "unit": m2['unit'],
            "total_kg_co2e": round(em2, 2)
        },
        "comparison": {
            "difference_kg": round(abs(em1 - em2), 2),
            "percent_difference": round(abs(em1 - em2) / max(em1, em2) * 100, 2),
            "higher_emitter": m1['display_name'] if em1 > em2 else m2['display_name']
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Starting EPA GHG Emissions Estimator API...")
    print(f"📊 Loaded {len(FACTOR_DICT)} emission factors")
    print(f"📁 Categories: {df['category'].unique().tolist()}")
    print("\n📍 API running at: http://localhost:8000")
    print("📖 API docs: http://localhost:8000/docs")
    print("\n⚡ Test with: curl http://localhost:8000/")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)