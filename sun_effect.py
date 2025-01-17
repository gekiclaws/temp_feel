# Import libraries
import pandas as pd
import numpy as np
from scipy.stats import ttest_ind
from sklearn.preprocessing import LabelEncoder
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns

# Load your dataset
df = pd.read_csv("temp feel - sorted.csv")

# Display the first few rows for reference
print("Dataset Head:")
print(df.head())

# Step 1: Data Preprocessing
print("\nStep 1: Data Preprocessing...")

# Replace NaN values with 0
df = df.fillna(0)

# Encode categorical variables
categorical_cols = ['headwind', 'daytime', 'feel_sun']  # Add others if necessary
label_encoders = {}

for col in categorical_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    label_encoders[col] = le

# Verify the cleaned dataset
print("\nCleaned Dataset Head (NaN replaced with 0):")
print(df.head())

# Step 2: Investigate the Relationship Between `feel_sun` and `hr`
print("\nStep 2: Investigating the relationship between `feel_sun` and `hr`...")
sun_hr_means = df.groupby('feel_sun')['hr'].mean()
print("\nAverage heart rate (hr) with and without sunlight exposure:")
print(sun_hr_means)

# Conduct a t-test to see if the difference is statistically significant
sun_yes = df[df['feel_sun'] == 1]['hr']
sun_no = df[df['feel_sun'] == 0]['hr']

if len(sun_yes) > 1 and len(sun_no) > 1:  # Ensure sufficient sample size
    t_stat, p_value = ttest_ind(sun_yes, sun_no)
    print("\nT-test Results for Heart Rate (hr) with Sun vs. No Sun:")
    print(f"T-statistic: {t_stat:.2f}, P-value: {p_value:.4f}")
    if p_value < 0.05:
        print("Result: Significant difference in heart rate due to sunlight exposure.")
    else:
        print("Result: No significant difference in heart rate due to sunlight exposure.")
else:
    print("\nT-test skipped: Insufficient sample size in one or both groups.")

# Step 3: Investigate the Interaction Between `feel_sun` and `hr` on `feels`
print("\nStep 3: Investigating the interaction between `feel_sun` and `hr` on `feels`...")

# Add an interaction term between `feel_sun` and `hr`
df['sun_hr_interaction'] = df['feel_sun'] * df['hr']

# Fit a logistic regression model to predict `feels` using `temp`, `hr`, `feel_sun`, and the interaction term
print("\nFitting a logistic regression model to analyze the interaction effect...")
X = df[['temp', 'hr', 'feel_sun', 'sun_hr_interaction']]
X = sm.add_constant(X)  # Add constant for the intercept
y = df['feels']

try:
    log_model = sm.Logit(y, X).fit()
    print("\nLogistic Regression Summary:")
    print(log_model.summary())
except Exception as e:
    print("\nError fitting logistic regression model:", e)

# Step 4: Visualize the Interaction Effect
print("\nStep 4: Visualizing the interaction between `feel_sun` and `hr`...")

# Create a scatter plot of `hr` vs. `temp` colored by `feel_sun` and styled by `feels`
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x='hr', y='temp', hue='feel_sun', style='feels', palette='viridis', s=100)
plt.title("Interaction Between Heart Rate, Sunlight, and Feels")
plt.xlabel("Heart Rate (hr)")
plt.ylabel("Temperature (temp)")
plt.legend(title="Legend")
plt.grid(True)
plt.show()

# Step 5: Summary and Next Steps
print("\nSummary of Findings:")
print("- If the p-value from the t-test is below 0.05, sunlight significantly impacts heart rate.")
print("- If the interaction term (`sun_hr_interaction`) in the logistic regression has a significant p-value, this indicates a compounding effect where sunlight amplifies the role of heart rate in determining thermal comfort.")
print("- The scatterplot provides a visual representation of how `feel_sun` and `hr` interact to influence perceived warmth (`feels`).")