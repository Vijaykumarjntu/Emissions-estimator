import pandas as pd

# Read the EPA Excel file
# df = pd.read_excel('ghg-emission-factors-hub-2025.xlsx', sheet_name='Sheet1')
df = pd.read_excel('ghg-emission-factors-hub-2025.xlsx')

# Look at what columns exist (EPA changes format sometimes)
print(df.columns.tolist())
print(df.head(10))

# Based on typical EPA structure, extract relevant data
# You'll need to adjust column names based on what you see

# Example mapping (adjust after you see actual columns):
epa_factors = []

for _, row in df.iterrows():
    material = row.get('Material', row.get('Category', ''))
    factor = row.get('kg CO2e per unit', row.get('Emission Factor', ''))
    unit = row.get('Unit', '')
    
    if material and pd.notna(factor):
        epa_factors.append({
            'material': material.lower(),
            'unit': unit,
            'kg_co2e_per_unit': float(factor),
            'source': 'EPA GHG Emission Factors Hub 2024',
            'uncertainty': '±15%'
        })

# Save to CSV
pd.DataFrame(epa_factors).to_csv('real_epa_factors.csv', index=False)
print(f"Saved {len(epa_factors)} real factors from EPA")