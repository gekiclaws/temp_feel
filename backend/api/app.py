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
    """Get paths for a specific model folder"""
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
        session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
        with open(meta_path, 'r') as f:
            metadata = json.load(f)
        return session, metadata
    except Exception as e:
        print(f"Error loading {model_name} model: {e}")
        return None, None

def load_scaler(scaler_filename):
    """Load scaler parameters (mean and scale) from a .npz file"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    scaler_path = os.path.join(base_dir, "models", scaler_filename)
    scaler_data = np.load(scaler_path)
    mean = scaler_data['mean']
    scale = scaler_data['scale']
    return mean, scale

# Load classifier model (for "feels") as before.
feels_model, feels_metadata = load_model('feels')

# Load the exported unsupervised clothing models
upper_model, upper_metadata = load_model('clothing_encoder')
lower_model, lower_metadata = load_model('clothing_pca')

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
        "temp", "sun", "headwind", "snow", "rain", "fatigued", "hr", "feels"
    ]
    X_raw = prepare_features(instances, raw_feature_names)

    # Split the features: first 7 are upper clothing; next 5 are lower clothing.
    # The remaining 8 features are for the classifier.
    upper_indices = list(range(0, 7))
    lower_indices = list(range(7, 12))
    classifier_rest_indices = list(range(12, 20))

    X_upper_raw = X_raw[:, upper_indices]  # shape (n,7)
    X_lower_raw = X_raw[:, lower_indices]  # shape (n,5)
    X_rest = X_raw[:, classifier_rest_indices]  # shape (n,8)

    # Normalize clothing features using saved scalers
    X_upper_norm = (X_upper_raw - upper_mean) / upper_scale
    X_lower_norm = (X_lower_raw - lower_mean) / lower_scale

    # Process clothing features through unsupervised models to get insulation features.
    upper_input_name = upper_model.get_inputs()[0].name
    lower_input_name = lower_model.get_inputs()[0].name
    upr_clo = upper_model.run(None, {upper_input_name: X_upper_norm})[0]  # shape (n,1)
    lwr_clo = lower_model.run(None, {lower_input_name: X_lower_norm})[0]    # shape (n,1)

    # Combine the unsupervised outputs with the remaining features.
    # Final classifier input order: upr_clo, lwr_clo, then [temp, sun, headwind, snow, rain, fatigued, hr, feels]
    X_classifier = np.concatenate([upr_clo, lwr_clo, X_rest], axis=1)

    # Run classifier model
    classifier_input_name = feels_model.get_inputs()[0].name
    outputs = feels_model.run(None, {classifier_input_name: X_classifier})
    predictions = outputs[0]  # First output: class predictions
    probabilities = outputs[1] if len(outputs) > 1 else None

    # Convert numpy outputs to lists for JSON serialization.
    predictions = predictions.tolist() if isinstance(predictions, np.ndarray) else predictions
    probabilities = probabilities.tolist() if isinstance(probabilities, np.ndarray) else probabilities

    # Map numeric classes to labels using classifier metadata.
    class_mapping = feels_metadata['class_mapping']
    prediction_labels = [class_mapping[str(int(p))] for p in predictions]
    prediction_label = prediction_labels[0]

    print("Prediction:", prediction_label, "Probabilities:", probabilities)
    return jsonify({
        "prediction": prediction_label,
        "probabilities": probabilities,
        "model_accuracy": feels_metadata.get("accuracy", 0.0)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)