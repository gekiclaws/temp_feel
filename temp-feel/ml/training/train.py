import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
import os
import pickle
import json
from datetime import datetime

# Simple configuration
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../models/feels/")
os.makedirs(MODEL_DIR, exist_ok=True)
VERSION = datetime.now().strftime("%Y%m%d_%H%M%S")
MODEL_PATH = os.path.join(MODEL_DIR, f"model_{VERSION}.pkl")
META_PATH = os.path.join(MODEL_DIR, "model_meta.json")
LATEST_PATH = os.path.join(MODEL_DIR, "latest_version.txt")

def train_model():
    """Train and save the random forest model"""
    # Load data
    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/cleaned_data.csv")
    df = pd.read_csv(data_path)
    print(f"Loaded {df.shape[0]} samples")
    
    # Prepare data
    X = df.drop('feels', axis=1)
    y = df['feels']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
    
    # Train model with simple hyperparameter tuning
    param_grid = {
        'n_estimators': [50, 100, 200],
        'max_depth': [None, 10, 20]
    }
    
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
    
    # Save model
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)
    
    # Save metadata
    metadata = {
        'version': VERSION,
        'accuracy': float(accuracy),
        'timestamp': datetime.now().isoformat(),
        'feature_names': X.columns.tolist(),
        'class_mapping': {0: 'cold', 1: 'cool', 2: 'warm', 3: 'hot'}
    }
    
    with open(META_PATH, 'w') as f:
        json.dump(metadata, f)
    
    with open(LATEST_PATH, 'w') as f:
        f.write(VERSION)
    
    print(f"Model saved to {MODEL_PATH}")
    return model, metadata

if __name__ == "__main__":
    train_model()