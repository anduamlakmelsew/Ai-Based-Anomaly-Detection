import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder
import joblib

# Load dataset
df = pd.read_csv("datasets/system_logs/loghub/HDFS/HDFS_2k.log_structured.csv")

print("Dataset shape:", df.shape)

# Use EventId as feature
encoder = LabelEncoder()
df["EventId_encoded"] = encoder.fit_transform(df["EventId"])

X = df[["EventId_encoded"]]

# Train model
model = IsolationForest(contamination=0.05, random_state=42)
model.fit(X)

# Save model and encoder
joblib.dump(model, "../models/system/system_model.pkl")
joblib.dump(encoder, "../models/system/system_encoder.pkl")

print("✅ System model trained and saved!")
