import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
import os
import pickle
import json
from datetime import datetime

# Base configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "../data/cleaned_data.csv")

def get_model_paths(target_name):
    """Generate model paths for a specific target feature"""
    model_dir = os.path.join(BASE_DIR, f"../models/{target_name}/")
    os.makedirs(model_dir, exist_ok=True)
    version = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    return {
        'dir': model_dir,
        'version': version,
        'model_path': os.path.join(model_dir, f"model_{version}.pkl"),
        'meta_path': os.path.join(model_dir, "model_meta.json"),
        'latest_path': os.path.join(model_dir, "latest_version.txt")
    }

def load_data():
    """Load and return the dataset"""
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {df.shape[0]} samples")
    return df

def train_classifier(target_name, feature_cols=None, param_grid=None, test_size=0.25):
    """Train a RandomForestClassifier for a categorical target variable"""
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
    
    # Evaluate
    accuracy = model.score(X_test, y_test)
    print(f"Model accuracy: {accuracy:.4f}")
    
    # Get unique class values and create mapping
    classes = sorted(y.unique())
    class_mapping = {i: str(val) for i, val in enumerate(classes)}
    
    # Get paths for this target
    paths = get_model_paths(target_name)
    
    # Save model
    with open(paths['model_path'], 'wb') as f:
        pickle.dump(model, f)
    
    # Save metadata
    metadata = {
        'version': paths['version'],
        'target': target_name,
        'model_type': 'classifier',
        'accuracy': float(accuracy),
        'timestamp': datetime.now().isoformat(),
        'feature_names': X.columns.tolist(),
        'class_mapping': class_mapping,
        'best_params': clf.best_params_
    }
    
    with open(paths['meta_path'], 'w') as f:
        json.dump(metadata, f)
    
    with open(paths['latest_path'], 'w') as f:
        f.write(paths['version'])
    
    print(f"Model saved to {paths['model_path']}")
    return model, metadata

def train_regressor(target_name, feature_cols=None, param_grid=None, test_size=0.25):
    """Train a RandomForestRegressor for a numerical target variable"""
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
        RandomForestRegressor(random_state=42),
        param_grid,
        cv=5,
        n_jobs=-1
    )
    
    clf.fit(X_train, y_train)
    model = clf.best_estimator_
    
    # Evaluate
    r2_score = model.score(X_test, y_test)
    print(f"Model R² score: {r2_score:.4f}")
    
    # Get paths for this target
    paths = get_model_paths(target_name)
    
    # Save model
    with open(paths['model_path'], 'wb') as f:
        pickle.dump(model, f)
    
    # Save metadata
    metadata = {
        'version': paths['version'],
        'target': target_name,
        'model_type': 'regressor',
        'r2_score': float(r2_score),
        'timestamp': datetime.now().isoformat(),
        'feature_names': X.columns.tolist(),
        'best_params': clf.best_params_
    }
    
    with open(paths['meta_path'], 'w') as f:
        json.dump(metadata, f)
    
    with open(paths['latest_path'], 'w') as f:
        f.write(paths['version'])
    
    print(f"Model saved to {paths['model_path']}")
    return model, metadata

def train_feels_model():
    """Train the original 'feels' model (for backward compatibility)"""
    # Define class mapping specific to 'feels'
    class_mapping = {0: 'cold', 1: 'cool', 2: 'warm', 3: 'hot'}
    
    # Train model
    model, metadata = train_classifier('feels')
    
    # Update metadata with the specific class mapping
    paths = get_model_paths('feels')
    metadata['class_mapping'] = class_mapping
    
    with open(paths['meta_path'], 'w') as f:
        json.dump(metadata, f)
    
    return model, metadata

# Train a model to predict heart rate (hr)
def train_hr_model():
    """Train a model to predict heart rate (hr)"""
    print("Training heart rate prediction model...")
    
    # Custom hyperparameter grid focused on regression performance
    param_grid = {
        'n_estimators': [100, 200, 300],
        'max_depth': [None, 15, 30],
        'min_samples_leaf': [1, 2, 4]
    }
    
    # Train the regression model
    model, metadata = train_regressor(
        target_name='hr',
        param_grid=param_grid,
        test_size=0.2  # Using a slightly different test size
    )
    
    print(f"Heart rate model training complete with R² score: {metadata['r2_score']:.4f}")
    return model, metadata

# Train a model to predict upper clothing insulation (upr_clo)
def train_upper_clo_model():
    """Train a model to predict upper clothing insulation (upr_clo)"""
    print("Training upper clothing insulation prediction model...")
    
    # Custom hyperparameter grid for this specific task
    param_grid = {
        'n_estimators': [100, 150, 200],
        'max_depth': [10, 20, None],
        'min_samples_split': [2, 5, 10]
    }
    
    # Train the regression model
    model, metadata = train_regressor(
        target_name='upr_clo',
        param_grid=param_grid
    )
    
    print(f"Upper clothing insulation model training complete with R² score: {metadata['r2_score']:.4f}")
    return model, metadata

if __name__ == "__main__":
    # Example usage
    train_feels_model()  # Train the original 'feels' model
    train_hr_model()         # Numerical heart rate model
    train_upper_clo_model()  # Numerical clothing insulation model