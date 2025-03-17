# Temp Feel API

A predictive system that correlates clothing choices with physiological data and weather conditions to optimize outdoor comfort.

## Prerequisites

- Python 3.x + pip
- Node.js and npm
- Java 11+ (for Java client)

## Setup and Installation

### API Setup
1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```

2. Open requirements.txt and uncomment the developer dependenices, then install them:
   ```bash
   vim requirements.txt
   pip install -r requirements.txt
   ```

3. Review `data/parameters.csv` to understand the dataset parameters and their meanings

4. Data preparation:
   - Replace `data/cleaned_data.csv` with your own data following the same schema or use as is for testing
   - Ensure your data matches the format in `parameters.csv`

5. Train the prediction models:
   ```bash
   python3 training/parse_cleaned_data.py
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

3. In `src/api-service.js`, set `API_BASE_URL` to `http:localhost:8080`.

4. Start the React development server:
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
2. Fill in the required information:
   - Temperature
   - Environmental conditions (sun, wind, precipitation)
   - Heart rate and fatigue level
   - Current clothing

## Troubleshooting

- If the API isn't responding, check if the Flask server is running on port 8080
- For data-related issues, verify your CSV file matches the expected schema
- For Java client issues, ensure Java 11+ is installed

## Contributing

Feel free to submit issues and enhancement requests!
