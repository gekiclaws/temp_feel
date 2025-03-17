import numpy as np
import pandas as pd
import tensorflow as tf
import random
import os
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import scipy.stats

# 🟢 Load your CSV dataset
file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/cleaned_data.csv")  # 🔹 Change this to your actual file path
data = pd.read_csv(file_path)

# 🟢 Define expected Clo values for validation
expected_clo = {
    "t_dress": 0.05, "t_poly": 0.08, "t_cot": 0.09, "sleeves": 0.20,
    "j_light": 0.50, "j_fleece": 0.70, "j_down": 0.90,
    "shorts": 0.06, "p_thin": 0.15, "p_thick": 0.24, "p_fleece": 0.80, "p_down": 0.90
}

# 🟢 Separate upper and lower body clothing
upper_clothing_features = ["t_dress", "t_poly", "t_cot", "sleeves", "j_light", "j_fleece", "j_down"]
lower_clothing_features = ["shorts", "p_thin", "p_thick", "p_fleece", "p_down"]

X_upper = data[upper_clothing_features]
X_lower = data[lower_clothing_features]

# 🟢 Normalize the data
scaler_upper = StandardScaler()
scaler_lower = StandardScaler()
X_upper_scaled = scaler_upper.fit_transform(X_upper)
X_lower_scaled = scaler_lower.fit_transform(X_lower)

# 🟢 Set random seeds for reproducibility
SEED = 42
np.random.seed(SEED)
random.seed(SEED)
tf.random.set_seed(SEED)
os.environ['PYTHONHASHSEED'] = str(SEED)

# 🟢 Force TensorFlow to use deterministic operations (CPU only)
tf.config.experimental.enable_op_determinism()

# 🟢 Define Autoencoder Model for Upper Body
def build_autoencoder(input_dim):
    input_layer = keras.Input(shape=(input_dim,))
    
    # Encoder (Deeper and No Dropout)
    encoded = layers.Dense(32, activation="relu")(input_layer)
    encoded = layers.Dense(16, activation="relu")(encoded)
    encoded = layers.Dense(8, activation="relu")(encoded)
    encoded = layers.Dense(4, activation="relu")(encoded)
    bottleneck = layers.Dense(1, activation="linear")(encoded)  # Single insulation feature

    # Decoder (Deeper for Better Reconstruction)
    decoded = layers.Dense(4, activation="relu")(bottleneck)
    decoded = layers.Dense(8, activation="relu")(decoded)
    decoded = layers.Dense(16, activation="relu")(decoded)
    decoded = layers.Dense(32, activation="relu")(decoded)
    output_layer = layers.Dense(input_dim, activation="linear")(decoded)

    autoencoder = keras.Model(input_layer, output_layer)
    encoder = keras.Model(input_layer, bottleneck)  # Extracts the learned insulation feature

    autoencoder.compile(optimizer=keras.optimizers.Adam(learning_rate=0.0005), loss="mse")
    return autoencoder, encoder

# 🟢 Train Autoencoder for Upper Body (More Complex Interactions)
autoencoder_upper, encoder_upper = build_autoencoder(X_upper_scaled.shape[1])
autoencoder_upper.fit(X_upper_scaled, X_upper_scaled, epochs=300, batch_size=16, verbose=1)

# 🟢 Use PCA for Lower Body (Since PCA is as Good as Autoencoder Here)
pca_lower = PCA(n_components=1)
lwr_clo_pca = pca_lower.fit_transform(X_lower_scaled)

# 🟢 Extract insulation features
data["upr_clo"] = encoder_upper.predict(X_upper_scaled)  # Rename to final format
data["lwr_clo"] = lwr_clo_pca  # PCA for Lower Body (Renamed)

# 🟢 Compute expected insulation values for validation
expected_upper_insulation = np.dot(X_upper, np.array([expected_clo[f] for f in upper_clothing_features]))
expected_lower_insulation = np.dot(X_lower, np.array([expected_clo[f] for f in lower_clothing_features]))

# 🟢 Compute correlation between Autoencoder/PCA insulation and expected Clo values
corr_upper, p_upper = scipy.stats.pearsonr(data["upr_clo"], expected_upper_insulation)
corr_lower, p_lower = scipy.stats.pearsonr(data["lwr_clo"], expected_lower_insulation)

# 🟢 Systematically Correct Flipped Signage
if corr_upper < 0:
    print("⚠️ Upper Body Autoencoder correlation is negative. Flipping sign...")
    data["upr_clo"] *= -1
    corr_upper, p_upper = scipy.stats.pearsonr(data["upr_clo"], expected_upper_insulation)

if corr_lower < 0:
    print("⚠️ Lower Body PCA correlation is negative. Flipping sign...")
    data["lwr_clo"] *= -1
    corr_lower, p_lower = scipy.stats.pearsonr(data["lwr_clo"], expected_lower_insulation)

# 🔬 Print corrected correlation results
print("\n🔬 **Validation of Final Insulation Features**")
print(f"✅ Upper Body Autoencoder Correlation (Fixed): {corr_upper:.3f} (p={p_upper:.3f})")
print(f"✅ Lower Body PCA Correlation (Fixed): {corr_lower:.3f} (p={p_lower:.3f})")

# 🟢 Retain only necessary columns for final dataset
final_columns = ["upr_clo", "lwr_clo", "temp", "sun", "headwind", "snow", "rain", "fatigued", "hr", "feels"]
data = data[final_columns]

# 🟢 Save the cleaned and formatted dataset
output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/computed_data.csv")
data.to_csv(output_file, index=False, sep=",")  # Save as tab-separated for readability
print(f"✅ Processed dataset saved as {output_file}")