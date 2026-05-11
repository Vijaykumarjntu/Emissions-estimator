# 🌍 EPA GHG Emissions Estimator API

A production-ready REST API for calculating greenhouse gas emissions using official **EPA GHG Emission Factors Hub 2025** data.

## 📊 Overview

This API provides access to **167 emission factors** across **12 EPA tables**, enabling accurate Scope 1, 2, and 3 emissions calculations for:

- 🔥 Stationary Combustion (coal, natural gas, biomass)
- 🚗 Mobile Combustion (diesel, gasoline, jet fuel)
- ✈️ Business Travel (cars, rail, air travel)
- 🗑️ Waste Management (recycling vs landfill)
- ⚡ Electricity by US region (eGRID)
- 🚛 Freight Transportation
- ❄️ Refrigerants & GWP values

## 🚀 Quick Start

### Local Development

```bash
# Clone repository
git clone https://github.com/yourusername/emission-estimator.git
cd emission-estimator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run API
python app.py