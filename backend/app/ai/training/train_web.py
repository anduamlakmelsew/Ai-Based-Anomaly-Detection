import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import pickle
import os

# ----------------------------
# Load CLEAN dataset
# ----------------------------
df = pd.read_parquet("processed/web_features_clean.parquet")

print("Dataset shape:", df.shape)

# ----------------------------
# Split features & labels
# ----------------------------
X = df.drop(columns=["label"])
y = df["label"]

# ----------------------------
# Train / Test split
# ----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print("Training samples:", X_train.shape[0])
print("Testing samples:", X_test.shape[0])

# ----------------------------
# Model (strong baseline)
# ----------------------------
model = RandomForestClassifier(
    n_estimators=300,
    max_depth=None,
    random_state=42,
    n_jobs=-1
)

print("Training model...")

model.fit(X_train, y_train)

# ----------------------------
# Evaluation
# ----------------------------
y_pred = model.predict(X_test)

print("\n📊 Classification Report:\n")
print(classification_report(y_test, y_pred))

print("\n📉 Confusion Matrix:\n")
print(confusion_matrix(y_test, y_pred))

# ----------------------------
# Save model
# ----------------------------
os.makedirs("../models", exist_ok=True)

with open("../models/web_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("\n✅ Model saved at: ai/models/web_model.pkl")
