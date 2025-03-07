from flask import Flask, request, jsonify
import pickle
import pandas as pd
import os
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_model_paths(model_name):
    """Get paths for a specific model"""
    model_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"models/{model_name}/")
    meta_path = os.path.join(model_dir, "model_meta.json")
    latest_path = os.path.join(model_dir, "latest_version.txt")
    return model_dir, meta_path, latest_path

def load_model(model_name):
    """Load the latest model and metadata for given model name"""
    try:
        model_dir, meta_path, latest_path = get_model_paths(model_name)
        
        with open(latest_path, 'r') as f:
            version = f.read().strip()
        
        model_path = os.path.join(model_dir, f"model_{version}.pkl")
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        with open(meta_path, 'r') as f:
            metadata = json.load(f)
        
        return model, metadata
    except Exception as e:
        print(f"Error loading {model_name} model: {e}")
        return None, None

# Load models
feels_model, feels_metadata = load_model('feels')
clothing_model, clothing_metadata = load_model('clothing')

@app.route("/predict-feels", methods=["POST"])
def predict_feels():
    if feels_model is None:
        print("No feels model loaded")
        return jsonify({"error": "No feels model loaded"}), 503
    
    data = request.json
    print(data)
    instances = data["instances"]
    
    # Convert to DataFrame
    df = pd.DataFrame(instances)
    
    # Ensure correct feature order
    feature_names = feels_metadata['feature_names']
    for feature in feature_names:
        if feature not in df.columns:
            df[feature] = 0
    
    df = df[feature_names]
    
    # Make prediction
    predictions = feels_model.predict(df).tolist()
    probabilities = feels_model.predict_proba(df).tolist()
    
    # Map numeric classes to labels
    class_mapping = feels_metadata['class_mapping']
    prediction_labels = [class_mapping[str(p)] for p in predictions]
    prediction_label = prediction_labels[0]

    print(probabilities)
    
    return jsonify({
        "prediction": prediction_label,
        "probabilities": probabilities
    })

@app.route("/predict-clothing", methods=["POST"])
def predict_clothing():
    if clothing_model is None:
        print("No clothing model loaded")
        return jsonify({"error": "No clothing model loaded"}), 503
    
    data = request.json
    print(data)
    instances = data["instances"]
    
    # Convert to DataFrame
    df = pd.DataFrame(instances)
    
    # Ensure correct feature order
    feature_names = clothing_metadata['feature_names']
    for feature in feature_names:
        if feature not in df.columns:
            df[feature] = 0
    
    df = df[feature_names]
    
    # Make prediction
    predictions = clothing_model.predict(df).tolist()
    
    # Get target column names
    target_cols = clothing_metadata['target_columns']
    
    # Format predictions as dict mapping target names to values
    prediction_dict = {}
    for i, col in enumerate(target_cols):
        prediction_dict[col] = predictions[0][i]
    print(prediction_dict)
    
    return jsonify({
        "predictions": prediction_dict
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)