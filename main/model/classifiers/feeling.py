# Import libraries
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder

# Load your dataset
df = pd.read_csv("temp feel - sorted.csv")
df = df.fillna(0)

# Display the first few rows of the dataset
print("First few rows of the dataset:")
print(df.head())

# Step 1: Preprocessing
# Identify all categorical columns and encode them
categorical_cols = ['feel_sun', 'precip', 'snow', 'headwind', 'fatigued']  # Include all necessary categorical columns
label_encoders = {}

for col in categorical_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    label_encoders[col] = le

# Encode the target variable ('feels')
target_encoder = LabelEncoder()
df['feels'] = target_encoder.fit_transform(df['feels'])

# Step 2: Use all features for training (except the target variable)
features = df.columns.difference(['feels'])  # Automatically select all columns except 'feels'
X = df[features]
y = df['feels']

# Debugging: Display the features being used
print("\nFeatures used for training:")
print(features)

# Step 3: Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 4: Train the Random Forest Classifier
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# Step 5: Make predictions
y_pred = rf_model.predict(X_test)

# Step 6: Evaluate the model
print("\n=== Model Evaluation ===")
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))
print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))

# Feature importance
feature_importances = pd.DataFrame({
    'Feature': X.columns,
    'Importance': rf_model.feature_importances_
}).sort_values(by='Importance', ascending=False)

print("\nFeature Importances:\n", feature_importances)

# Decode Predictions (Optional)
# decoded_predictions = target_encoder.inverse_transform(y_pred)
# print("\nDecoded Predictions:\n", decoded_predictions)