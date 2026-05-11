# fixed_epa_parser.py
import pandas as pd
import re

def parse_epa_excel_fixed(file_path):
    """
    Parse EPA Excel where data starts in column B (index 1)
    """
    
    df = pd.read_excel(file_path, sheet_name='Emission Factors Hub', header=None)
    
    all_factors = []
    current_table = None
    current_headers = None
    current_data = []
    
    for idx in range(len(df)):
        # Look at column B (index 1) for table markers
        cell_b = df.iloc[idx, 1] if len(df.columns) > 1 and not pd.isna(df.iloc[idx, 1]) else ""
        cell_c = df.iloc[idx, 2] if len(df.columns) > 2 and not pd.isna(df.iloc[idx, 2]) else ""
        
        cell_b_str = str(cell_b).strip() if cell_b else ""
        cell_c_str = str(cell_c).strip() if cell_c else ""
        
        # Look for "Table X" in column B
        match = re.search(r'Table\s+(\d+)', cell_b_str, re.IGNORECASE)
        
        if match:
            # Save previous table
            if current_table and current_data and current_headers:
                print(f"✅ Table {current_table}: {len(current_data)} rows")
                # Process the table data
                for row in current_data:
                    if row and len(row) >= 3:
                        factor = None
                        for val in row:
                            if isinstance(val, (int, float)) and not pd.isna(val):
                                factor = val
                                break
                        
                        if factor and row[0]:
                            all_factors.append({
                                'material': str(row[0]).lower().replace(' ', '_').replace('(', '').replace(')', '')[:50],
                                'display_name': str(row[0])[:50],
                                'factor': float(factor),
                                'unit': row[2] if len(row) > 2 and row[2] else 'unknown',
                                'table': current_table,
                                'category': get_category(current_table)
                            })
            
            # Start new table
            current_table = int(match.group(1))
            current_headers = None
            current_data = []
            print(f"\n📌 Found Table {current_table} at row {idx}")
            
            # Find headers (look ahead for non-empty row with text)
            for offset in range(1, 10):
                if idx + offset >= len(df):
                    break
                header_row = df.iloc[idx + offset]
                headers = []
                for col in range(1, 8):  # Columns B through H
                    val = header_row[col] if col < len(header_row) and not pd.isna(header_row[col]) else None
                    if val:
                        headers.append(str(val).strip())
                if len(headers) >= 2:
                    current_headers = headers
                    print(f"   Headers at row {idx+offset}: {headers[:3]}")
                    break
            
            continue
        
        # Collect data if we're in a table
        if current_table and cell_c_str and not cell_b_str.startswith('Table'):
            # Check if this row has numeric data
            has_number = False
            row_data = []
            
            for col in range(1, 8):  # Columns B through H
                val = df.iloc[idx, col] if col < len(df.columns) else None
                if isinstance(val, (int, float)) and not pd.isna(val):
                    has_number = True
                row_data.append(val)
            
            if has_number and row_data[0]:  # First column should have material name
                current_data.append(row_data)
    
    # Save last table
    if current_table and current_data:
        for row in current_data:
            if row and len(row) >= 3:
                factor = None
                for val in row:
                    if isinstance(val, (int, float)) and not pd.isna(val):
                        factor = val
                        break
                
                if factor and row[0]:
                    all_factors.append({
                        'material': str(row[0]).lower().replace(' ', '_').replace('(', '').replace(')', '')[:50],
                        'display_name': str(row[0])[:50],
                        'factor': float(factor),
                        'unit': row[2] if len(row) > 2 and row[2] else 'unknown',
                        'table': current_table,
                        'category': get_category(current_table)
                    })
        print(f"✅ Table {current_table}: {len(current_data)} rows")
    
    return all_factors

def get_category(table_num):
    categories = {
        1: "Stationary Combustion",
        2: "Mobile Combustion CO2",
        3: "Mobile Combustion CH4/N2O",
        6: "Electricity",
        8: "Transportation",
        9: "Waste",
        10: "Business Travel",
        11: "Global Warming Potential",
        12: "Refrigerants"
    }
    return categories.get(table_num, f"Table {table_num}")

# Run it
if __name__ == "__main__":
    factors = parse_epa_excel_fixed("ghg-emission-factors-hub-2025.xlsx")
    
    print(f"\n{'='*60}")
    print(f"✅ TOTAL FACTORS EXTRACTED: {len(factors)}")
    
    if factors:
        df_factors = pd.DataFrame(factors)
        df_factors.to_csv("all_epa_factors.csv", index=False)
        print(f"💾 Saved to all_epa_factors.csv")
        print(f"\n📋 Preview:")
        print(df_factors.head(20).to_string())
        
        # Show what tables we got
        print(f"\n📊 Tables extracted:")
        for table_num, group in df_factors.groupby('table'):
            print(f"   Table {table_num}: {len(group)} factors")