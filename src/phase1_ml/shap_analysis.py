import os
import joblib
import pandas as pd
import shap
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

PROJECT_DIR = r"C:\GeoSense_Agent"

DATA_FILE = os.path.join(
    PROJECT_DIR,
    "data",
    "processed",
    "labelled_sites.csv"
)

MODEL_FILE = os.path.join(
    PROJECT_DIR,
    "models",
    "saved",
    "site_scorer_model.pkl"
)

OUTPUT_DIR = os.path.join(
    PROJECT_DIR,
    "outputs",
    "reports"
)

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "shap_importance.png"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load dataset
df = pd.read_csv(DATA_FILE)

# Features used during model training
FEATURES = [
    "dist_road_m",
    "dist_hospital_m",
    "flood_risk"
]

X = df[FEATURES]
y = df["label"]

# Same train/test split used during training
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

# Load trained model
model = joblib.load(MODEL_FILE)

print("Loaded model:", type(model))
print("Test samples:", len(X_test))

# Create SHAP explainer
explainer = shap.TreeExplainer(model)

# Calculate SHAP values
shap_values = explainer.shap_values(X_test)

# Handle binary-class SHAP output
if isinstance(shap_values, list):
    shap_values_to_plot = shap_values[1]
else:
    shap_values_to_plot = shap_values

# Create SHAP summary plot
plt.figure()

shap.summary_plot(
    shap_values_to_plot,
    X_test,
    show=False
)

plt.tight_layout()

# Save figure
plt.savefig(
    OUTPUT_FILE,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print()
print("SHAP analysis completed successfully.")
print("SHAP plot saved to:")
print(OUTPUT_FILE)