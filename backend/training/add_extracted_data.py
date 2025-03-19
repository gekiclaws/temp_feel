
import os

def append_and_clear_data():
    input_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/extracted_data.csv")
    output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/cleaned_data.csv")
    try:
        # Read the extracted data
        with open(input_file, 'r') as extracted_file:
            lines = extracted_file.readlines()
            # Skip the header (first line) if there are lines
            extracted_content = ''.join(lines[1:] if lines else []).strip()
            
        if extracted_content:  # Only proceed if there's content to append
            # Append the extracted data to cleaned_data.csv
            with open(output_file, 'a') as cleaned_file:
                # If the extracted content doesn't start with a newline, add one
                if not extracted_content.startswith('\n'):
                    cleaned_file.write('\n')
                cleaned_file.write(extracted_content)
            
            # Clear the extracted_data.csv file
            with open(input_file, 'w') as extracted_file:
                extracted_file.write('')
                
            print("Data successfully appended and extracted file cleared")
        else:
            print("No data to append - extracted file is empty")
            
    except FileNotFoundError as e:
        print(f"Error: Required file not found - {e}")
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    append_and_clear_data()