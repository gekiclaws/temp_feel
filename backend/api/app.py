import os
import json

import onnxruntime as ort
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_model_path(onnx_filename, model_name=None):
    """
    Constructs the full path to an ONNX file.
    
    If model_name is provided, the file is expected to reside in models/<model_name>/.
    Otherwise, the file is assumed to be in the root of the models/ directory.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if model_name:
        model_dir = os.path.join(base_dir, "models", model_name)
    else:
        model_dir = os.path.join(base_dir, "models")
    return os.path.join(model_dir, onnx_filename)

def load_onnx_model(onnx_filename, model_name=None):
    """
    Load an ONNX model.
    
    Parameters:
      onnx_filename (str): The filename of the ONNX model.
      model_name (str, optional): The subfolder name under models/ where the file is located.
                                  If omitted, the file is loaded from the root of models/.
    Returns:
      An ONNX InferenceSession or None if loading fails.
    """
    model_path = get_model_path(onnx_filename, model_name)
    try:
        session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
        return session
    except Exception as e:
        print(f"Error loading ONNX model from '{model_path}': {e}")
        return None

def load_classifier_model(model_name):
    """
    Load a classifier model along with its metadata.
    
    Assumes that the classifier ONNX file is named "model.onnx" and is stored in models/<model_name>/,
    and that the metadata is stored in a file called "model_meta.json" in the same folder.
    """
    session = load_onnx_model("model.onnx", model_name=model_name)
    if session is None:
        return None, None
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    meta_path = os.path.join(base_dir, "models", model_name, "model_meta.json")
    try:
        with open(meta_path, 'r') as f:
            metadata = json.load(f)
    except Exception as e:
        print(f"Error loading metadata for model '{model_name}': {e}")
        metadata = None
    return session, metadata

def load_scaler(scaler_filename):
    """Load scaler parameters (mean and scale) from a .npz file and cast to float32."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    scaler_path = os.path.join(base_dir, "models", scaler_filename)
    scaler_data = np.load(scaler_path)
    mean = scaler_data['mean'].astype(np.float32)
    scale = scaler_data['scale'].astype(np.float32)
    return mean, scale

# Load classifier model "feels" from models/feels/
feels_model, feels_metadata = load_classifier_model('feels')

# Load preprocessing models stored in the root of models/ with specific filenames.
upper_model = load_onnx_model("encoder_upper.onnx")
lower_model = load_onnx_model("pca_lower.onnx")

# Load scaler parameters for clothing normalization
upper_mean, upper_scale = load_scaler("scaler_upper.npz")
lower_mean, lower_scale = load_scaler("scaler_lower.npz")

def prepare_features(instances, feature_names):
    """Convert list of instance dictionaries to a numpy array with features in the given order"""
    X = np.zeros((len(instances), len(feature_names)), dtype=np.float32)
    for i, instance in enumerate(instances):
        for j, feature in enumerate(feature_names):
            X[i, j] = float(instance.get(feature, 0))
    return X

def index_to_label(index, metadata):
    """Convert a class index to a label using the class mapping in the metadata"""
    return metadata["class_mapping"].get(str(index), "Unknown")

## API ##

@app.route('/')
def home():
    return 'Hello, World!'

@app.route("/predict/feels", methods=["POST"])
def predict_feels():
    if feels_model is None:
        print("No feels model loaded")
        return jsonify({"error": "No feels model loaded"}), 503

    data = request.json
    print("Received data:", data)
    instances = data["instances"]

    # Updated raw input schema: 12 clothing features + 8 remaining features
    raw_feature_names = [
        "t_dress", "t_poly", "t_cot", "sleeves", "j_light", "j_fleece", "j_down",
        "shorts", "p_thin", "p_thick", "p_fleece", "p_down",
        "temp", "sun", "headwind", "snow", "rain", "fatigued", "hr"
    ]
    X_raw = prepare_features(instances, raw_feature_names)

    # Split the features: first 7 are upper clothing; next 5 are lower clothing.
    # The remaining 8 features are for the classifier.
    upper_indices = list(range(0, 7))
    lower_indices = list(range(7, 12))
    classifier_rest_indices = list(range(12, 19))

    X_upper_raw = X_raw[:, upper_indices]  # shape (n,7)
    X_lower_raw = X_raw[:, lower_indices]  # shape (n,5)
    X_rest = X_raw[:, classifier_rest_indices]  # shape (n,7)

    # Normalize clothing features using saved scalers
    X_upper_norm = (X_upper_raw - upper_mean) / upper_scale
    X_lower_norm = (X_lower_raw - lower_mean) / lower_scale

    # Process clothing features through unsupervised models to get insulation features.
    upper_input_name = upper_model.get_inputs()[0].name
    lower_input_name = lower_model.get_inputs()[0].name
    upr_clo = upper_model.run(None, {upper_input_name: X_upper_norm})[0]  # shape (n,1)
    lwr_clo = lower_model.run(None, {lower_input_name: X_lower_norm})[0]    # shape (n,1)

    # Combine the unsupervised outputs with the remaining features.
    # Final classifier input order: upr_clo, lwr_clo, then [temp, sun, headwind, snow, rain, fatigued, hr]
    X_classifier = np.concatenate([upr_clo, lwr_clo, X_rest], axis=1)

    # Run classifier model
    classifier_input_name = feels_model.get_inputs()[0].name
    outputs = feels_model.run(None, {classifier_input_name: X_classifier})
    predictions = outputs[0]  # First output: class predictions
    probabilities = outputs[1] if len(outputs) > 1 else None

    # Convert numpy outputs to lists for JSON serialization.
    predictions = predictions.tolist() if isinstance(predictions, np.ndarray) else predictions
    probabilities = probabilities.tolist() if isinstance(probabilities, np.ndarray) else probabilities
    prediction_label = index_to_label(predictions[0], feels_metadata)
    accuracy = feels_metadata.get("accuracy", 0.0)

    print("Prediction:", prediction_label, "\nProbabilities:", probabilities, "\nAccuracy:", accuracy)
    return jsonify({
        "prediction": prediction_label,
        "probabilities": probabilities,
        "accuracy": accuracy
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)