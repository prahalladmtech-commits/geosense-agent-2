import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

from xgboost import XGBClassifier


# --------------------------------------------------
# Paths
# --------------------------------------------------

DATA_FILE = r"C:\GeoSense_Agent\data\processed\labelled_sites.csv"

MODEL_DIR = r"C:\GeoSense_Agent\models\saved"
MODEL_FILE = os.path.join(
    MODEL_DIR,
    "site_scorer_model.pkl"
)

os.makedirs(MODEL_DIR, exist_ok=True)


# --------------------------------------------------
# Load labelled data
# --------------------------------------------------

print("Loading labelled dataset...")

df = pd.read_csv(DATA_FILE)

print("Dataset shape:", df.shape)

# Features currently available in your dataset
FEATURES = [
    "dist_road_m",
    "dist_hospital_m",
    "flood_risk"
]

X = df[FEATURES]
y = df["label"]


# --------------------------------------------------
# Train/test split
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))


# --------------------------------------------------
# Random Forest
# --------------------------------------------------

print("\nTraining Random Forest...")

rf = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

rf.fit(X_train, y_train)

rf_pred = rf.predict(X_test)

rf_accuracy = accuracy_score(
    y_test,
    rf_pred
)

print("Random Forest accuracy:",
      rf_accuracy)

print(
    classification_report(
        y_test,
        rf_pred
    )
)


# --------------------------------------------------
# XGBoost
# --------------------------------------------------

print("\nTraining XGBoost...")

xgb = XGBClassifier(
    n_estimators=100,
    random_state=42,
    eval_metric="logloss"
)

xgb.fit(X_train, y_train)

xgb_pred = xgb.predict(X_test)

xgb_accuracy = accuracy_score(
    y_test,
    xgb_pred
)

print("XGBoost accuracy:",
      xgb_accuracy)

print(
    classification_report(
        y_test,
        xgb_pred
    )
)


# --------------------------------------------------
# Select best model
# --------------------------------------------------

if xgb_accuracy > rf_accuracy:
    best_model = xgb
    best_name = "XGBoost"
    best_accuracy = xgb_accuracy
else:
    best_model = rf
    best_name = "Random Forest"
    best_accuracy = rf_accuracy


print("\nBest model:", best_name)
print("Best accuracy:", best_accuracy)


# --------------------------------------------------
# Save model
# --------------------------------------------------

joblib.dump(
    best_model,
    MODEL_FILE
)

print("\nModel saved successfully:")
print(MODEL_FILE)