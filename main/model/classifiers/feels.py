import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import classification_report, confusion_matrix
from sklearn2pmml import sklearn2pmml
from sklearn2pmml.pipeline import PMMLPipeline
from joblib import dump
import os

def load_data(file_path="../training/data/cleaned_data.csv"):
    # Get the directory where the current script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Calculate the path to the data file relative to the script
    data_path = os.path.join(script_dir, file_path)

    # Normalize the path to resolve the ../ references
    data_path = os.path.normpath(data_path)

    try:
        df = pd.read_csv(data_path)
        print(f"Data loaded successfully with {df.shape[0]} rows and {df.shape[1]} columns")
        return df
    except Exception as e:
        print(f"Error: {e}")

def train_random_forest(df):
    # Split features and target
    X = df.drop('feels', axis=1)
    y = df['feels']
    
    # Split into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y if len(y.unique()) > 1 else None)
    
    print(f"Training set: {X_train.shape[0]} samples")
    print(f"Testing set: {X_test.shape[0]} samples")
    
    # Initial Random Forest model
    rf = RandomForestClassifier(random_state=42)
    
    # Perform cross-validation to estimate model performance
    cv_scores = cross_val_score(rf, X_train, y_train, cv=5, scoring='accuracy')
    print(f"Cross-validation accuracy: {np.mean(cv_scores):.4f} ± {np.std(cv_scores):.4f}")
    
    # Hyperparameter tuning using GridSearchCV
    param_grid = {
        'n_estimators': [50, 100, 200],
        'max_depth': [None, 10, 20, 30],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4]
    }
    
    # If dataset is small, use a simpler grid
    if X_train.shape[0] < 20:
        param_grid = {
            'n_estimators': [10, 50],
            'max_depth': [None, 5],
            'min_samples_split': [2],
            'min_samples_leaf': [1]
        }
    
    print("Performing hyperparameter tuning...")
    grid_search = GridSearchCV(
        estimator=rf,
        param_grid=param_grid,
        cv=min(5, len(np.unique(y_train))),  # Ensure CV doesn't exceed number of classes
        scoring='accuracy',
        n_jobs=-1
    )
    
    grid_search.fit(X_train, y_train)
    
    print(f"Best parameters: {grid_search.best_params_}")
    best_rf = grid_search.best_estimator_
    
    # Create a PMML pipeline
    pmml_pipeline = PMMLPipeline([
        ("classifier", best_rf)
    ])
    
    # Fit the pipeline with your data
    X = df.drop('feels', axis=1)
    y = df['feels']
    pmml_pipeline.fit(X, y)
    
    # Export to PMML
    sklearn2pmml(pmml_pipeline, "artifacts/feels/random_forest_feels.pmml", with_repr=True)
    print("Model exported as PMML to model/random_forest_feels.pmml")
    
    # Evaluate on test set
    y_pred = best_rf.predict(X_test)
    
    print("\nModel Evaluation on Test Set:")
    print(f"Accuracy: {best_rf.score(X_test, y_test):.4f}")
    
    # Print classification report if there are multiple classes in the test set
    if len(np.unique(y_test)) > 1:
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
    
    # Print confusion matrix
    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(cm)
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'Feature': X.columns,
        'Importance': best_rf.feature_importances_
    }).sort_values('Importance', ascending=False)
    
    print("\nFeature Importance:")
    print(feature_importance)
    
    # Save the model
    model_filename = 'artifacts/feels/random_forest_feels_classifier.joblib'
    dump(best_rf, model_filename)
    print(f"\nModel saved as {model_filename}")
    
    # Save the feature names for future reference
    feature_names_file = 'artifacts/feels/feature_names.txt'
    with open(feature_names_file, 'w') as f:
        f.write(','.join(X.columns))
    print(f"Feature names saved as {feature_names_file}")
    
    # Save the feels mapping for future reference
    feels_map = {i: label for i, label in enumerate(['cold', 'cool', 'warm', 'hot'])}
    feels_map_file = 'artifacts/feels/feels_mapping.txt'
    with open(feels_map_file, 'w') as f:
        for i, label in feels_map.items():
            f.write(f"{i},{label}\n")
    print(f"Feels mapping saved as {feels_map_file}")
    
    return best_rf, X, y, feature_importance

def main():
    # Load the data
    df = load_data()
    
    # Print basic info about the dataset
    print("\nDataset Overview:")
    print(df.head())
    print("\nData Types:")
    print(df.dtypes)
    print("\nMissing Values:")
    print(df.isnull().sum())
    print("\nFeels Distribution:")
    print(df['feels'].value_counts())
    
    # Check if we have enough data for each class
    min_samples = df['feels'].value_counts().min()
    if min_samples < 3:
        print(f"\nWarning: The minimum class has only {min_samples} samples. Model performance may be poor.")
    
    # Train the model
    model, X, y, feature_importance = train_random_forest(df)
    
    print("\nModel training and evaluation complete!")

if __name__ == "__main__":
    main()