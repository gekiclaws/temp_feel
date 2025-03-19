import os
import json
import pickle
import pandas as pd
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV

import onnx
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

# Base configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "../data/computed_data.csv")

def get_model_paths(target_name):
    """Generate model paths for a specific target feature."""
    model_dir = os.path.join(BASE_DIR, f"../models/{target_name}/")
    os.makedirs(model_dir, exist_ok=True)
    version = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    return {
        'dir': model_dir,
        'version': version,
        'model_path': os.path.join(model_dir, f"model.pkl"),
        'meta_path': os.path.join(model_dir, "model_meta.json"),
        'latest_path': os.path.join(model_dir, "latest_version.txt")
    }

def load_data():
    """Load and return the dataset."""
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {df.shape[0]} samples")
    return df

def convert_model_to_onnx(model, metadata, paths):
    """Convert the trained model to ONNX format and save it."""
    n_features = len(metadata['feature_names'])
    initial_type = [('float_input', FloatTensorType([None, n_features]))]
    onx = convert_sklearn(model, initial_types=initial_type)
    
    # Ensure the ONNX model uses IR version 9
    onnx_model = onnx.load_model_from_string(onx.SerializeToString())
    onnx_model.ir_version = 9
    onnx.checker.check_model(onnx_model)
    
    output_path = os.path.join(paths['dir'], 'model.onnx')
    with open(output_path, 'wb') as f:
        f.write(onnx_model.SerializeToString())
        
    print(f"Successfully converted model to ONNX with IR version 9. Saved at {output_path}")

def train_classifier(target_name, feature_cols=None, param_grid=None, test_size=0.25):
    """Train a RandomForestClassifier for a categorical target variable."""
    # Load data
    df = load_data()
    
    # Determine features to use
    if feature_cols is None:
        feature_cols = [col for col in df.columns if col != target_name]
    
    # Prepare data
    X = df[feature_cols]
    y = df[target_name]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
    
    # Default param grid if none provided
    if param_grid is None:
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [None, 10, 20]
        }
    
    # Train model with hyperparameter tuning
    clf = GridSearchCV(
        RandomForestClassifier(random_state=42),
        param_grid,
        cv=5,
        n_jobs=-1
    )
    
    clf.fit(X_train, y_train)
    model = clf.best_estimator_
    
    # Evaluate model
    accuracy = model.score(X_test, y_test)
    print(f"Model accuracy: {accuracy:.4f}")
    
    # Compute feature importances if available
    if hasattr(model, 'feature_importances_'):
        feature_importances = dict(zip(X.columns, model.feature_importances_))
        print("Feature importances:")
        for feature, importance in feature_importances.items():
            print(f"  {feature}: {importance:.4f}")
    else:
        feature_importances = {}
    
    # Map numeric class values to descriptive labels
    feels_labels = {
        0: 'cold',
        1: 'cool',
        2: 'warm', 
        3: 'hot'
    }
    classes = sorted(y.unique())
    class_mapping = {str(val): feels_labels[val] for val in classes}
    
    # Get file paths for saving the model and metadata
    paths = get_model_paths(target_name)
    
    # Save the trained model
    with open(paths['model_path'], 'wb') as f:
        pickle.dump(model, f)
    
    # Save metadata (including feature importances)
    metadata = {
        'version': paths['version'],
        'target': target_name,
        'model_type': 'classifier',
        'accuracy': float(accuracy),
        'timestamp': datetime.now().isoformat(),
        'feature_names': X.columns.tolist(),
        'feature_importances': feature_importances,
        'class_mapping': class_mapping,
        'best_params': clf.best_params_
    }
    
    with open(paths['meta_path'], 'w') as f:
        json.dump(metadata, f)
    
    with open(paths['latest_path'], 'w') as f:
        f.write(paths['version'])
    
    print(f"Model saved to {paths['model_path']}")
    
    # Convert the trained model to ONNX format
    convert_model_to_onnx(model, metadata, paths)
    
    return model, metadata

def train_feels_model():
    """Train the model for predicting 'feels' value."""
    print("Training 'feels' prediction model...")
    
    # Train model
    model, metadata = train_classifier('feels')
    
    print(f"Feels model training complete with accuracy: {metadata['accuracy']:.4f}")
    print(f"Class mapping: {metadata['class_mapping']}")
    return model, metadata

if __name__ == "__main__":
    # Import new data before training if available
    input_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/raw_data.txt")
    # check if raw_data file is empty
    if os.path.getsize(input_file) > 0:
        import parse_raw_data, add_extracted_data, parse_cleaned_data
        parse_raw_data.extract_and_clear_data()
        add_extracted_data.append_and_clear_data()
        parse_cleaned_data.main()

    # Train all models
    train_feels_model()