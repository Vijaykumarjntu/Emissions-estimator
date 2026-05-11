# final_complete_parser.py
import pandas as pd
import re

def parse_all_tables(file_path):
    """Parse ALL tables from EPA Excel file"""
    
    df = pd.read_excel(file_path, sheet_name='Emission Factors Hub', header=None)
    all_factors = []
    
    # Table 1: Stationary Combustion (rows 16-34)
    print("\n📌 Table 1: Stationary Combustion")
    for idx in range(16, 35):  # Anthracite through Wood and Wood Residuals
        material = df.iloc[idx, 2] if not pd.isna(df.iloc[idx, 2]) else None
        factor = df.iloc[idx, 4] if not pd.isna(df.iloc[idx, 4]) else None
        
        if material and factor and material not in ['Coal and Coke', 'Other Fuels - Solid', 'Biomass Fuels - Solid', 'Natural Gas', 'Other Fuels - Gaseous', 'Biomass Fuels - Gaseous', 'Petroleum Products', 'Biomass Fuels - Liquid']:
            all_factors.append({
                'material': str(material).lower().replace(' ', '_').replace('(', '').replace(')', ''),
                'display_name': str(material),
                'factor': float(factor),
                'unit': 'kg CO2 per mmBtu',
                'table': 1,
                'category': 'Stationary Combustion'
            })
    print(f"   ✅ Extracted {len([f for f in all_factors if f['table']==1])} factors")
    
    # Table 2: Mobile Combustion CO2 (rows 103-112)
    print("\n📌 Table 2: Mobile Combustion CO2")
    for idx in range(103, 113):
        material = df.iloc[idx, 2] if not pd.isna(df.iloc[idx, 2]) else None
        factor = df.iloc[idx, 3] if not pd.isna(df.iloc[idx, 3]) else None
        unit = df.iloc[idx, 4] if not pd.isna(df.iloc[idx, 4]) else "gallon"
        
        if material and factor and material != 'Fuel Type':
            all_factors.append({
                'material': str(material).lower().replace(' ', '_').replace('(', '').replace(')', '').replace('%', 'percent'),
                'display_name': str(material),
                'factor': float(factor),
                'unit': str(unit),
                'table': 2,
                'category': 'Mobile Combustion CO2'
            })
    print(f"   ✅ Extracted {len([f for f in all_factors if f['table']==2])} factors")
    
    # Table 3: Mobile Combustion CH4 and N2O (Gasoline Vehicles)
    print("\n📌 Table 3: Gasoline Vehicle CH4/N2O")
    current_vehicle = None
    for idx in range(126, 174):  # Gasoline Passenger Cars through 2022
        vehicle = df.iloc[idx, 2] if not pd.isna(df.iloc[idx, 2]) else None
        year = df.iloc[idx, 3] if not pd.isna(df.iloc[idx, 3]) else None
        ch4 = df.iloc[idx, 4] if not pd.isna(df.iloc[idx, 4]) else None
        
        if vehicle and vehicle != 'Gasoline Passenger Cars' and 'Gasoline' in str(vehicle):
            current_vehicle = vehicle
        elif ch4 and year:
            all_factors.append({
                'material': f"{current_vehicle or 'gasoline_vehicle'}_{str(year).replace('-', '_')}".lower().replace(' ', '_'),
                'display_name': f"{current_vehicle or 'Vehicle'} ({year})",
                'factor': float(ch4),
                'unit': 'g CH4 per vehicle-mile',
                'table': 3,
                'category': 'Mobile Combustion CH4 (Gasoline)'
            })
    print(f"   ✅ Extracted {len([f for f in all_factors if f['table']==3])} factors")
    
    # Table 6: Electricity (rows 338-357)
    print("\n📌 Table 6: Electricity by Region")
    for idx in range(338, 358):
        region = df.iloc[idx, 2] if not pd.isna(df.iloc[idx, 2]) else None
        factor = df.iloc[idx, 4] if not pd.isna(df.iloc[idx, 4]) else None
        
        if region and factor and region not in ['eGRID Subregion Acronym', 'AKGD']:
            all_factors.append({
                'material': str(region).lower(),
                'display_name': str(region),
                'factor': float(factor),
                'unit': 'lb CO2 per MWh',
                'table': 6,
                'category': 'Electricity (eGRID)'
            })
    print(f"   ✅ Extracted {len([f for f in all_factors if f['table']==6])} factors")
    
    # Table 7: Steam and Heat (row 409)
    print("\n📌 Table 7: Steam and Heat")
    factor = df.iloc[409, 3] if not pd.isna(df.iloc[409, 3]) else None
    if factor:
        all_factors.append({
            'material': 'steam_and_heat',
            'display_name': 'Steam and Heat',
            'factor': float(factor),
            'unit': 'kg CO2 per mmBtu',
            'table': 7,
            'category': 'Steam and Heat'
        })
    print(f"   ✅ Extracted {len([f for f in all_factors if f['table']==7])} factors")
    
    # Table 8: Transportation (rows 421-427)
    print("\n📌 Table 8: Transportation")
    for idx in range(421, 428):
        vehicle = df.iloc[idx, 2] if not pd.isna(df.iloc[idx, 2]) else None
        factor = df.iloc[idx, 3] if not pd.isna(df.iloc[idx, 3]) else None
        
        if vehicle and factor:
            all_factors.append({
                'material': str(vehicle).lower().replace(' ', '_').replace('(', '').replace(')', ''),
                'display_name': str(vehicle),
                'factor': float(factor),
                'unit': 'kg CO2 per vehicle-mile',
                'table': 8,
                'category': 'Transportation'
            })
    print(f"   ✅ Extracted {len([f for f in all_factors if f['table']==8])} factors")
    
    # Table 9: Waste Management (rows 435-455)
    print("\n📌 Table 9: Waste Management")
    for idx in range(435, 456):
        material = df.iloc[idx, 2] if not pd.isna(df.iloc[idx, 2]) else None
        factor = df.iloc[idx, 3] if not pd.isna(df.iloc[idx, 3]) else None
        
        if material and factor and material != 'Material':
            all_factors.append({
                'material': str(material).lower().replace(' ', '_').replace('/', '_'),
                'display_name': str(material),
                'factor': float(factor),
                'unit': 'metric tons CO2e per short ton',
                'table': 9,
                'category': 'Waste Management (Recycled)'
            })
    print(f"   ✅ Extracted {len([f for f in all_factors if f['table']==9])} factors")
    
    # Table 10: Business Travel (rows 503-514)
    print("\n📌 Table 10: Business Travel")
    for idx in range(503, 515):
        vehicle = df.iloc[idx, 2] if not pd.isna(df.iloc[idx, 2]) else None
        factor = df.iloc[idx, 3] if not pd.isna(df.iloc[idx, 3]) else None
        
        if vehicle and factor and vehicle != 'Vehicle Type':
            unit = 'passenger-mile' if 'rail' in str(vehicle).lower() or 'bus' in str(vehicle).lower() or 'air' in str(vehicle).lower() else 'vehicle-mile'
            all_factors.append({
                'material': str(vehicle).lower().replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_').replace('<', '').replace('>', ''),
                'display_name': str(vehicle),
                'factor': float(factor),
                'unit': unit,
                'table': 10,
                'category': 'Business Travel'
            })
    print(f"   ✅ Extracted {len([f for f in all_factors if f['table']==10])} factors")
    
    # Table 11: GWP Values (rows 523-544)
    print("\n📌 Table 11: Global Warming Potential")
    for idx in range(523, 545):
        gas = df.iloc[idx, 2] if not pd.isna(df.iloc[idx, 2]) else None
        gwp = df.iloc[idx, 4] if not pd.isna(df.iloc[idx, 4]) else None
        
        if gas and gwp:
            all_factors.append({
                'material': str(gas).lower().replace(' ', '_').replace('-', '_'),
                'display_name': str(gas),
                'factor': float(gwp),
                'unit': 'GWP (100-year)',
                'table': 11,
                'category': 'Global Warming Potential'
            })
    print(f"   ✅ Extracted {len([f for f in all_factors if f['table']==11])} factors")
    
    # Table 12: Refrigerants (rows 560-581)
    print("\n📌 Table 12: Refrigerants")
    for idx in range(560, 582):
        refrigerant = df.iloc[idx, 2] if not pd.isna(df.iloc[idx, 2]) else None
        gwp = df.iloc[idx, 3] if not pd.isna(df.iloc[idx, 3]) else None
        
        if refrigerant and gwp and 'R-' in str(refrigerant):
            all_factors.append({
                'material': str(refrigerant).lower(),
                'display_name': str(refrigerant),
                'factor': float(gwp),
                'unit': 'GWP (100-year)',
                'table': 12,
                'category': 'Refrigerants'
            })
    print(f"   ✅ Extracted {len([f for f in all_factors if f['table']==12])} factors")
    
    return all_factors

# Run it
if __name__ == "__main__":
    factors = parse_all_tables("ghg-emission-factors-hub-2025.xlsx")
    
    print(f"\n{'='*60}")
    print(f"✅ TOTAL FACTORS EXTRACTED: {len(factors)}")
    
    if factors:
        df_factors = pd.DataFrame(factors)
        df_factors.to_csv("all_epa_factors.csv", index=False)
        print(f"💾 Saved to all_epa_factors.csv")
        
        print(f"\n📊 Summary by table:")
        for table_num in sorted(df_factors['table'].unique()):
            group = df_factors[df_factors['table'] == table_num]
            print(f"   Table {table_num} - {group.iloc[0]['category']}: {len(group)} factors")
        
        print(f"\n📋 Sample data (first 20 rows):")
        print(df_factors[['display_name', 'factor', 'unit', 'table']].head(20).to_string())