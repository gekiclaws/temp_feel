import re
import csv
import pandas as pd
import os

def parse_notes(notes):
    results = []
    
    for line in notes.strip().split('\n'):
        # Skip empty lines
        if not line.strip():
            continue
            
        # Initialize all fields with default values
        record = {
            't_polo': 0, 't_poly': 0, 't_cot': 0,
            'sleeves': 0, 'j_light': 0, 'j_fleece': 0, 'j_down': 0,
            'shorts': 0, 'p_thin': 0, 'p_thick': 0, 'p_fleece': 0, 'p_down': 0,
            'temp': 0, 'sun': 0, 'headwind': 0, 'snow': 0, 'rain': 0,
            'fatigued': 0, 'hr': 0, 'feels': 1  # Default 'feels' to cool (1)
        }
        
        # Split the line into parts for processing
        parts = line.strip().split(',')
        
        # Process the first part (clothing type and modifiers)
        if parts:
            first_part = parts[0].strip().split()
            if first_part:
                # Determine clothing type
                clothing_type = first_part[0].lower()
                if 'polo' in clothing_type:
                    record['t_polo'] = 1
                elif 'poly' in clothing_type:
                    record['t_poly'] = 1
                elif 'cot' in clothing_type:
                    record['t_cot'] = 1
                
                # Process modifiers in the first part
                for item in first_part[1:]:
                    # Upper body modifiers (lowercase)
                    if item == 's':
                        record['sleeves'] = 1
                    elif item == 'l':
                        record['j_light'] = 1
                    elif item == 'f':
                        record['j_fleece'] = 1
                    elif item == 'd':
                        record['j_down'] = 1
                    
                    # Lower body clothing (uppercase)
                    elif item == 'S':
                        record['shorts'] = 1
                    elif item == 'T':
                        record['p_thick'] = 1
                    elif item == 'L':
                        record['p_thin'] = 1
                    elif item == 'F':
                        record['p_fleece'] = 1
                    elif item == 'D':
                        record['p_down'] = 1
        
        # Process all parts for other information
        for part in parts:
            part = part.strip().lower()
            
            # Extract temperature
            temp_match = re.search(r'(-?\d+)c?', part)
            if temp_match:
                record['temp'] = int(temp_match.group(1))
            
            # Extract heart rate (looking for standalone 2-3 digit numbers)
            hr_match = re.search(r'\b(\d{2,3})\b', part)
            if hr_match and not re.search(r'[a-zA-Z]', part):  # Avoid matching temp with c
                record['hr'] = int(hr_match.group(1))
            
            # Check for sun condition
            if 'sun' in part:
                if 'no sun' not in part:
                    record['sun'] = 1
            
            # Check for headwind
            if 'head' in part or 'headwind' in part:  # Fixed logical error here
                record['headwind'] = 1
            
            # Check for fatigue
            if 'fatigue' in part:
                record['fatigued'] = 1
            
            # Check for rain with intensity
            if 'rain' in part:
                if 'heavy rain' in part:
                    record['rain'] = 3
                elif 'medium rain' in part:
                    record['rain'] = 2
                elif 'light rain' in part:
                    record['rain'] = 1
                else:
                    record['rain'] = 1  # default to light if just "rain"
            
            # Check for snow with intensity
            if 'snow' in part:
                if 'heavy snow' in part:
                    record['snow'] = 3
                elif 'medium snow' in part:
                    record['snow'] = 2
                elif 'light snow' in part:
                    record['snow'] = 1
                else:
                    record['snow'] = 1  # default to light if just "snow"
            
            # Check for feels
            if 'cold' in part and not any(x in part for x in ['no', 'not']):
                record['feels'] = 0
            elif 'cool' in part and not any(x in part for x in ['no', 'not']):
                record['feels'] = 1
            elif 'warm' in part and not any(x in part for x in ['no', 'not']):
                record['feels'] = 2
            elif 'hot' in part and not any(x in part for x in ['no', 'not']):
                record['feels'] = 3
        
        results.append(record)
    
    return results

def write_csv(records, output_file):
    fields = [
        't_polo', 't_poly', 't_cot', 'sleeves', 'j_light', 'j_fleece', 'j_down',
        'shorts', 'p_thin', 'p_thick', 'p_fleece', 'p_down', 'temp', 'sun',
        'headwind', 'snow', 'rain', 'fatigued', 'hr', 'feels'
    ]
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)
    
    print(f"Data written to {output_file}")
    
    # Create a pandas DataFrame for preview
    df = pd.DataFrame(records)
    return df

def main():
    input_file = "data/raw_data.txt"
    output_file = "data/parsed_data.csv"
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        print("Creating a sample raw_data.txt file with example data...")
        
        # Create a sample file with example data
        sample_data = """polo d F, 1c, 70, no sun, .25 rain, cool
polo F, 1c, 100, no sun, cool
cot L, -10c, 110, no sun, light snow, cool
poly L, -19c 120, no sun, cool
cot T, -17 110 sun cool
cot T, -17 70 sun headwind cool
cot d T -15 70 sun cool
poly d T -16 110 no sun cool sun warm
poly T -10 110 sun cool
cot F -12 110 sun cool
cot L -2 95 sun cool
poly L -6 110, medium rain, sun cool"""
        
        with open(input_file, 'w') as f:
            f.write(sample_data)
        
        print(f"Sample '{input_file}' created. You can edit this file and run the script again.")
    
    # Read the input file
    try:
        with open(input_file, 'r') as f:
            notes = f.read()
        
        print(f"Successfully read {len(notes.strip().split())} words from '{input_file}'")
        
        # Parse the notes and write to CSV
        records = parse_notes(notes)
        df = write_csv(records, output_file)
        
        # Display a preview of the data
        print("\nPreview of the formatted data:")
        print(df.head())
        
        # Display summary statistics
        print("\nSummary statistics:")
        print(df.describe())
        
        # Print frequency counts for categorical variables
        print("\nCounts for categorical variables:")
        for col in ['t_polo', 't_poly', 't_cot', 'sleeves', 'j_light', 'j_fleece', 
                    'j_down', 'shorts', 'p_thin', 'p_thick', 'p_fleece', 'p_down',
                    'sun', 'headwind', 'fatigued', 'snow', 'rain', 'feels']:
            print(f"{col}:\n{df[col].value_counts()}")
        
        print(f"\nProcessing complete. Data saved to '{output_file}'")
        
    except Exception as e:
        print(f"Error processing the file: {e}")

if __name__ == "__main__":
    main()