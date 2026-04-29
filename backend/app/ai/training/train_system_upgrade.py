import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib

# Load dataset
df = pd.read_csv("datasets/system_logs/loghub/HDFS/HDFS_2k.log_structured.csv")

print("Dataset shape:", df.shape)

# Use EventTemplate (IMPORTANT)
logs = df["EventTemplate"].astype(str)

# Convert text → numerical features
vectorizer = TfidfVectorizer(max_features=1000)
X = vectorizer.fit_transform(logs)

print("TF-IDF shape:", X.shape)

# Train Isolation Forest
model = IsolationForest(contamination=0.05, random_state=42)
model.fit(X)

# Save everything
joblib.dump(model, "../models/system/system_model.pkl")
joblib.dump(vectorizer, "../models/system/system_vectorizer.pkl")

print("✅ Upgraded system model trained and saved!")
