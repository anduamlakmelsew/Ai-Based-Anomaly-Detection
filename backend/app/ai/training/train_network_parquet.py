import pandas as pd
import glob
import os
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

# -------------------------
# 1. Load all parquet files
# -------------------------
files = glob.glob("processed/network_parquet/*.parquet")

df_list = []
for file in files:
    print(f"Loading {file}")
    df_list.append(pd.read_parquet(file))

df = pd.concat(df_list, ignore_index=True)

print("\nTotal dataset shape:", df.shape)

# -------------------------
# 2. Features & Label
# -------------------------
X = df.drop(columns=["label"])
y = df["label"]

# -------------------------
# 3. Preprocessing
# -------------------------
X = pd.get_dummies(X)
X = X.fillna(0)

# -------------------------
# 4. Train/Test Split
# -------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("\nTrain shape:", X_train.shape)
print("Test shape:", X_test.shape)

# -------------------------
# 5. Train Model
# -------------------------
model = RandomForestClassifier(
    n_estimators=100,
    n_jobs=-1,
    random_state=42
)

model.fit(X_train, y_train)

# -------------------------
# 6. Evaluate
# -------------------------
y_pred = model.predict(X_test)

print("\nClassification Report:\n")
print(classification_report(y_test, y_pred))

print("\nConfusion Matrix:\n")
print(confusion_matrix(y_test, y_pred))

# -------------------------
# 7. Save Model + Features
# -------------------------
os.makedirs("../models", exist_ok=True)

joblib.dump(model, "../models/network_model.pkl")
joblib.dump(X.columns, "../models/network_features.pkl")

print("\nModel and features saved in ../models/")
