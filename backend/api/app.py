from flask import Flask, request, jsonify
from flask_cors import CORS
import onnxruntime as ort
import numpy as np
import os
import json

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return 'Hello, World!'

def get_model_paths(model_name):
    """Get paths for a specific model"""
    # Go up one directory from api/ to backend/
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_dir = os.path.join(base_dir, "models", model_name)
    meta_path = os.path.join(model_dir, "model_meta.json")
    model_path = os.path.join(model_dir, "model.onnx")
    return model_dir, meta_path, model_path

def load_model(model_name):
    """Load the ONNX model and metadata for given model name"""
    try:
        model_dir, meta_path, model_path = get_model_paths(model_name)
        
        # Load ONNX model
        session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
        
        # Load metadata
        with open(meta_path, 'r') as f:
            metadata = json.load(f)
        
        return session, metadata
    except Exception as e:
        print(f"Error loading {model_name} model: {e}")
        return None, None

# Load models
feels_model, feels_metadata = load_model('feels')
clothing_model, clothing_metadata = load_model('clothing')

def prepare_features(instances, feature_names):
    """Convert instances to numpy array with correct feature order"""
    # Initialize array with zeros
    X = np.zeros((len(instances), len(feature_names)), dtype=np.float32)  # ONNX requires float32
    
    # Fill in values for features that exist
    for i, instance in enumerate(instances):
        for j, feature in enumerate(feature_names):
            X[i, j] = float(instance.get(feature, 0))
    
    return X

@app.route("/predict/feels", methods=["POST"])
def predict_feels():
    if feels_model is None:
        print("No feels model loaded")
        return jsonify({"error": "No feels model loaded"}), 503
    
    data = request.json
    print(data)
    instances = data["instances"]
    
    # Convert to numpy array
    feature_names = feels_metadata['feature_names']
    X = prepare_features(instances, feature_names)
    
    # Get input name from model
    input_name = feels_model.get_inputs()[0].name
    
    # Make prediction
    outputs = feels_model.run(None, {input_name: X})
    predictions = outputs[0]  # Class predictions are first output
    probabilities = outputs[1] if len(outputs) > 1 else None  # Probabilities if available
    
    # Convert numpy arrays to lists for JSON serialization
    predictions = predictions.tolist() if isinstance(predictions, np.ndarray) else predictions
    probabilities = probabilities.tolist() if isinstance(probabilities, np.ndarray) else probabilities
    
    # Map numeric classes to labels
    class_mapping = feels_metadata['class_mapping']
    prediction_labels = [class_mapping[str(int(p))] for p in predictions]
    prediction_label = prediction_labels[0]

    print(prediction_label, probabilities)
    
    return jsonify({
        "prediction": prediction_label,
        "probabilities": probabilities
    })

@app.route("/predict/clothing", methods=["POST"])
def predict_clothing():
    if clothing_model is None:
        print("No clothing model loaded")
        return jsonify({"error": "No clothing model loaded"}), 503
    
    data = request.json
    print(data)
    instances = data["instances"]
    
    # Convert to numpy array
    feature_names = clothing_metadata['feature_names']
    X = prepare_features(instances, feature_names)
    
    # Get input name from model
    input_name = clothing_model.get_inputs()[0].name
    
    # Make prediction
    outputs = clothing_model.run(None, {input_name: X})
    predictions = outputs[0]  # Get first output
    
    # Convert numpy arrays to lists for JSON serialization
    predictions = predictions.tolist() if isinstance(predictions, np.ndarray) else predictions
    
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