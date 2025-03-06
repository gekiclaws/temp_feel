from flask import Flask, request, jsonify
import pickle
import pandas as pd
import os
import json

app = Flask(__name__)

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../classifiers/feels/")
META_PATH = os.path.join(MODEL_DIR, "model_meta.json")
LATEST_PATH = os.path.join(MODEL_DIR, "latest_version.txt")

def load_model():
    """Load the latest model and metadata"""
    try:
        with open(LATEST_PATH, 'r') as f:
            version = f.read().strip()
        
        model_path = os.path.join(MODEL_DIR, f"model_{version}.pkl")
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        with open(META_PATH, 'r') as f:
            metadata = json.load(f)
        
        return model, metadata
    except Exception as e:
        print(f"Error loading model: {e}")
        return None, None

model, metadata = load_model()

@app.route("/predict", methods=["POST"])
def predict():
    if model is None:
        return jsonify({"error": "No model loaded"}), 503
    
    data = request.json
    instances = data["instances"]
    
    # Convert to DataFrame
    df = pd.DataFrame(instances)
    
    # Ensure correct feature order
    feature_names = metadata['feature_names']
    for feature in feature_names:
        if feature not in df.columns:
            df[feature] = 0
    
    df = df[feature_names]
    
    # Make prediction
    predictions = model.predict(df).tolist()
    probabilities = model.predict_proba(df).tolist()
    
    # Map numeric classes to labels
    class_mapping = metadata['class_mapping']
    prediction_labels = [class_mapping[str(p)] for p in predictions]
    
    return jsonify({
        "predictions": predictions,
        "prediction_labels": prediction_labels,
        "probabilities": probabilities
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)