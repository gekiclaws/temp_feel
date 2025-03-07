# Temp Feel

A predictive system that correlates clothing choices with physiological data and weather conditions to optimize outdoor comfort.

## Prerequisites

- Python 3.x
- Node.js and npm
- Java 11+ (for Java client)
- Required Python packages (install via `pip install -r requirements.txt`):
  - Flask
  - pandas
  - scikit-learn
  - numpy

## Setup and Installation

### API Setup
1. Navigate to the `api` directory:
   ```bash
   cd api
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Review `data/parameters.csv` to understand the dataset parameters and their meanings

4. Data preparation:
   - Use the existing `data/cleaned_data.csv` for testing, or
   - Replace it with your own data following the same schema
   - Ensure your data matches the format in `parameters.csv`

5. Train the prediction models:
   ```bash
   python3 training/train.py
   ```

6. Start the Flask server:
   ```bash
   python3 app.py
   ```
   The API will be available at `http://localhost:8080`

### Frontend Setup
1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```

2. Install Node.js dependencies:
   ```bash
   npm install
   ```

3. Start the React development server:
   ```bash
   npm start
   ```
   The UI will be available at `http://localhost:3000`

### Java Client Setup
1. Navigate to the `api-java` directory:
   ```bash
   cd api-java
   ```

2. Build the project using Maven:
   ```bash
   mvn clean install
   ```

3. Check the `src/test/java/CLI.java` file for an example of how to use the Java client library (TempFeel) in your own applications.

## Usage

1. Open your browser and navigate to `http://localhost:3000`
2. Choose between two modes:
   - **Predict Comfort**: Input environmental conditions and clothing to predict comfort level
   - **Recommend Clothing**: Input conditions and current comfort to get clothing recommendations
3. Fill in the required information:
   - Temperature
   - Environmental conditions (sun, wind, precipitation)
   - Heart rate and fatigue level
   - Current clothing (for comfort prediction)
   - Comfort level (for clothing recommendations)

## Troubleshooting

- If the API isn't responding, check if the Flask server is running on port 8080
- If you see CORS errors, ensure the API is properly configured to accept requests from the frontend
- For data-related issues, verify your CSV file matches the expected schema
- For Java client issues, ensure Java 11+ is installed

## Contributing

Feel free to submit issues and enhancement requests!