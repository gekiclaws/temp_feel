import os
import json
import onnxruntime as ort
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_model_path(onnx_filename, model_name=None):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if model_name:
        model_dir = os.path.join(base_dir, "models", model_name)
    else:
        model_dir = os.path.join(base_dir, "models")
    model_path = os.path.join(model_dir, onnx_filename)
    
    print(f"🔍 Checking model path: {model_path}")
    
    if not os.path.exists(model_path):
        print(f"❌ ERROR: Model file not found at {model_path}")
    
    return model_path

def load_onnx_model(onnx_filename, model_name=None):
    model_path = get_model_path(onnx_filename, model_name)
    try:
        session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
        print(f"✅ Successfully loaded ONNX model: {onnx_filename}")
        return session
    except Exception as e:
        print(f"❌ Error loading ONNX model from '{model_path}': {e}")
        return None

def load_classifier_model(model_name):
    session = load_onnx_model("model.onnx", model_name=model_name)
    if session is None:
        print(f"❌ ERROR: Failed to load classifier model '{model_name}'")
        return None, None

    meta_path = get_model_path("model_meta.json", model_name)
    try:
        with open(meta_path, 'r') as f:
            metadata = json.load(f)
        print(f"✅ Successfully loaded metadata for '{model_name}'")
    except Exception as e:
        print(f"❌ Error loading metadata for model '{model_name}': {e}")
        metadata = None
    
    return session, metadata

def load_scaler(scaler_filename):
    scaler_path = get_model_path(scaler_filename)
    try:
        scaler_data = np.load(scaler_path)
        print(f"✅ Loaded scaler: {scaler_filename}")
        return scaler_data['mean'].astype(np.float32), scaler_data['scale'].astype(np.float32)
    except Exception as e:
        print(f"❌ Error loading scaler '{scaler_filename}': {e}")
        return None, None

print("🔍 Loading models...")

feels_model, feels_metadata = load_classifier_model('feels')
upper_model = load_onnx_model("encoder_upper.onnx")
lower_model = load_onnx_model("pca_lower.onnx")

upper_mean, upper_scale = load_scaler("scaler_upper.npz")
lower_mean, lower_scale = load_scaler("scaler_lower.npz")

if lower_model is None:
    raise RuntimeError("❌ CRITICAL ERROR: lower_model failed to load. Check logs.")

print("✅ All models loaded successfully.")

def prepare_features(instances, feature_names):
    X = np.zeros((len(instances), len(feature_names)), dtype=np.float32)
    for i, instance in enumerate(instances):
        for j, feature in enumerate(feature_names):
            X[i, j] = float(instance.get(feature, 0))
    return X

def index_to_label(index, metadata):
    return metadata["class_mapping"].get(str(index), "Unknown")

@app.route('/')
def home():
    return 'Hello, World!'

@app.route("/predict/feels", methods=["POST"])
def predict_feels():
    if feels_model is None:
        print("❌ No feels model loaded")
        return jsonify({"error": "No feels model loaded"}), 503

    data = request.json
    print("📩 Received data:", data)

    instances = data.get("instances", [])
    if not instances:
        return jsonify({"error": "No instances provided"}), 400

    raw_feature_names = [
        "t_dress", "t_poly", "t_cot", "sleeves", "j_light", "j_fleece", "j_down",
        "shorts", "p_thin", "p_thick", "p_fleece", "p_down",
        "temp", "sun", "headwind", "snow", "rain", "fatigued", "hr"
    ]
    X_raw = prepare_features(instances, raw_feature_names)

    upper_indices = list(range(0, 7))
    lower_indices = list(range(7, 12))
    classifier_rest_indices = list(range(12, 19))

    X_upper_raw = X_raw[:, upper_indices]
    X_lower_raw = X_raw[:, lower_indices]
    X_rest = X_raw[:, classifier_rest_indices]

    print("🔍 Normalizing features...")
    X_upper_norm = (X_upper_raw - upper_mean) / upper_scale
    X_lower_norm = (X_lower_raw - lower_mean) / lower_scale

    print("🔍 Checking lower model input shapes...")
    try:
        upper_input_name = upper_model.get_inputs()[0].name
        lower_input_name = lower_model.get_inputs()[0].name
        print(f"✅ Upper Model Input: {upper_input_name}, Shape: {upper_model.get_inputs()[0].shape}")
        print(f"✅ Lower Model Input: {lower_input_name}, Shape: {lower_model.get_inputs()[0].shape}")
    except Exception as e:
        print(f"❌ Model input shape retrieval error: {e}")
        return jsonify({"error": f"Model input shape retrieval failed: {e}"}), 500

    try:
        print("🚀 Running upper and lower models...")
        upr_clo = upper_model.run(None, {upper_input_name: X_upper_norm})[0]
        lwr_clo = lower_model.run(None, {lower_input_name: X_lower_norm})[0]
    except Exception as e:
        print(f"❌ Model execution error: {e}")
        return jsonify({"error": f"Model execution failed: {e}"}), 500

    print("🔍 Combining classifier inputs...")
    X_classifier = np.concatenate([upr_clo, lwr_clo, X_rest], axis=1)

    print("🚀 Running classifier model...")
    try:
        classifier_input_name = feels_model.get_inputs()[0].name
        outputs = feels_model.run(None, {classifier_input_name: X_classifier})
        predictions = outputs[0]
        probabilities = outputs[1] if len(outputs) > 1 else None
    except Exception as e:
        print(f"❌ Classifier model error: {e}")
        return jsonify({"error": f"Classifier model failed: {e}"}), 500

    predictions = predictions.tolist() if isinstance(predictions, np.ndarray) else predictions
    probabilities = probabilities.tolist() if isinstance(probabilities, np.ndarray) else probabilities
    prediction_label = index_to_label(predictions[0], feels_metadata)
    accuracy = feels_metadata.get("accuracy", 0.0)

    print("✅ Prediction:", prediction_label, "\n📊 Probabilities:", probabilities, "\n🎯 Accuracy:", accuracy)
    
    return jsonify({
        "prediction": prediction_label,
        "probabilities": probabilities,
        "accuracy": accuracy
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)