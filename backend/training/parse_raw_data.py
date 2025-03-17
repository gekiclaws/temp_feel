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
            't_dress': 0, 't_poly': 0, 't_cot': 0,
            'sleeves': 0, 'j_light': 0, 'j_fleece': 0, 'j_down': 0,
            'shorts': 0, 'p_thin': 0, 'p_thick': 0, 'p_fleece': 0, 'p_down': 0,
            'temp': 0, 'sun': 0, 'headwind': 0, 'snow': 0, 'rain': 0,
            'fatigued': 0, 'hr': 0, 'feels': 1  # Default 'feels' to cool (1)
        }

        if 'dress' in line:
            record['t_dress'] = 1
        elif 'poly' in line:
            record['t_poly'] = 1
        elif 'cot' in line:
            record['t_cot'] = 1

        if ' s ' in line:
            record['sleeves'] = 1
        elif ' l ' in line:
            record['j_light'] = 1
        elif ' f ' in line:
            record['j_fleece'] = 1
        elif ' d ' in line:
            record['j_down'] = 1

        if ' S ' in line:
            record['shorts'] = 1
        elif ' L ' in line:
            record['p_thin'] = 1
        elif ' T ' in line:
            record['p_thick'] = 1
        elif ' F ' in line:
            record['p_fleece'] = 1
        elif ' D ' in line:
            record['p_down'] = 1

        # Extract temperature
        # Look for temperature with 'c' suffix first
        temp_match = re.search(r'(-?\d+)c\b', line)
        if not temp_match:
            # Look for any number that could be a temperature (<=50)
            numbers = re.findall(r'\b(-?\d+)\b', line)
            for num in numbers:
                if int(num) <= 50:
                    temp_match = re.match(r'(-?\d+)', num)
                    break
        
        if temp_match:
            record['temp'] = int(temp_match.group(1))
        
        # Extract heart rate
        # Extract heart rate (looking for numbers above 50)
        numbers = re.findall(r'\b(\d+)\b', line)
        for num in numbers:
            if int(num) > 50:
                record['hr'] = int(num)
                break
        
        # Check for sun condition
        if 'sun' in line:
            if 'no sun' not in line:
                record['sun'] = 1
        
        # Check for headwind
        if 'head' in line or 'headwind' in line:
            record['headwind'] = 1
        
        # Check for fatigue
        if 'fatigue' in line:
            record['fatigued'] = 1
        
        # Check for rain with intensity
        if 'rain' in line:
            if 'heavy rain' in line:
                record['rain'] = 3
            elif 'medium rain' in line:
                record['rain'] = 2
            elif 'light rain' in line:
                record['rain'] = 1
            else:
                record['rain'] = 1  # default to light if just "rain"
        
        # Check for snow with intensity
        if 'snow' in line:
            if 'heavy snow' in line:
                record['snow'] = 3
            elif 'medium snow' in line:
                record['snow'] = 2
            elif 'light snow' in line:
                record['snow'] = 1
            else:
                record['snow'] = 1  # default to light if just "snow"

        # Check for feels
        if 'cold' in line:
            record['feels'] = 0
        elif 'cool' in line:
            record['feels'] = 1
        elif 'warm' in line:
            record['feels'] = 2
        elif 'hot' in line:
            record['feels'] = 3
        
        results.append(record)
    
    return results

def write_csv(records, output_file):
    fields = [
        't_dress', 't_poly', 't_cot', 'sleeves', 'j_light', 'j_fleece', 'j_down',
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
    input_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/raw_data.txt")
    output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/extracted_data.csv")
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
    
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
        for col in ['t_dress', 't_poly', 't_cot', 'sleeves', 'j_light', 'j_fleece', 
                    'j_down', 'shorts', 'p_thin', 'p_thick', 'p_fleece', 'p_down',
                    'sun', 'headwind', 'fatigued', 'snow', 'rain', 'feels']:
            print(f"{col}:\n{df[col].value_counts()}")
        
        print(f"\nProcessing complete. Data saved to '{output_file}'")
        
    except Exception as e:
        print(f"Error processing the file: {e}")

if __name__ == "__main__":
    main()