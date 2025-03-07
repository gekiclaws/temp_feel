from model_utils import train_classifier, train_regressor, train_multi_regressor

def train_feels_model():
    """Train the model for predicting 'feels' value"""
    print("Training 'feels' prediction model...")
    
    # Define class mapping specific to 'feels'
    class_mapping = {0: 'cold', 1: 'cool', 2: 'warm', 3: 'hot'}
    
    # Train model
    model, metadata = train_classifier('feels')
    
    # Update metadata with the specific class mapping
    metadata['class_mapping'] = class_mapping
    
    print(f"Feels model training complete with accuracy: {metadata['accuracy']:.4f}")
    return model, metadata

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

def train_clothing_model():
    """Train a model to predict both upper and lower clothing insulation"""
    print("Training clothing insulation prediction model...")
    
    # Define target columns for multi-output prediction
    target_cols = ['upr_clo', 'lwr_clo']
    
    # Custom hyperparameter grid
    param_grid = {
        'n_estimators': [100, 150, 200],
        'max_depth': [10, 20, None],
        'min_samples_split': [2, 5, 10]
    }
    
    # Train the multi-output regression model
    model, metadata = train_multi_regressor(
        target_name='clothing',
        target_cols=target_cols,
        param_grid=param_grid
    )
    
    print(f"Clothing model training complete!")
    print(f"  Combined R² score: {metadata['combined_r2_score']:.4f}")
    print(f"  Upper clothing R² score: {metadata['individual_r2_scores']['upr_clo']:.4f}")
    print(f"  Lower clothing R² score: {metadata['individual_r2_scores']['lwr_clo']:.4f}")
    
    return model, metadata

if __name__ == "__main__":
    # Train all models
    train_feels_model()
    train_hr_model()
    train_clothing_model()