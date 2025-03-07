import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import r2_score
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

def train_multi_regressor(target_name, target_cols, feature_cols=None, param_grid=None, test_size=0.25):
    """Train a RandomForestRegressor for multiple target variables"""
    # Load data
    df = load_data()
    
    # Determine features to use
    if feature_cols is None:
        feature_cols = [col for col in df.columns if col not in target_cols]
    
    # Prepare data
    X = df[feature_cols]
    y = df[target_cols].values  # Convert to numpy array for multi-output
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
    
    # Default param grid if none provided
    if param_grid is None:
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [None, 10, 20]
        }
    
    # Train model with hyperparameter tuning
    clf = GridSearchCV(
        RandomForestRegressor(random_state=42),  # Multi-output is supported natively
        param_grid,
        cv=5,
        n_jobs=-1
    )
    
    clf.fit(X_train, y_train)
    model = clf.best_estimator_
    
    # Evaluate
    y_pred = model.predict(X_test)
    combined_r2 = model.score(X_test, y_test)  # Overall R² score
    
    # Calculate individual R² scores for each target
    individual_r2_scores = {}
    for i, col in enumerate(target_cols):
        individual_r2_scores[col] = r2_score(y_test[:, i], y_pred[:, i])
        print(f"R² score for {col}: {individual_r2_scores[col]:.4f}")
    
    print(f"Combined R² score: {combined_r2:.4f}")
    
    # Get paths for this target
    paths = get_model_paths(target_name)
    
    # Save model
    with open(paths['model_path'], 'wb') as f:
        pickle.dump(model, f)
    
    # Save metadata
    metadata = {
        'version': paths['version'],
        'target': target_name,
        'target_columns': target_cols,
        'model_type': 'multi_output_regressor',
        'combined_r2_score': float(combined_r2),
        'individual_r2_scores': {k: float(v) for k, v in individual_r2_scores.items()},
        'timestamp': datetime.now().isoformat(),
        'feature_names': X.columns.tolist(),
        'best_params': clf.best_params_
    }
    
    with open(paths['meta_path'], 'w') as f:
        json.dump(metadata, f)
    
    with open(paths['latest_path'], 'w') as f:
        f.write(paths['version'])
    
    print(f"Multi-output model saved to {paths['model_path']}")
    return model, metadata