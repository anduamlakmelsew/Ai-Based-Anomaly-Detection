import joblib

# Load model + vectorizer
model = joblib.load("../models/system/system_model.pkl")
vectorizer = joblib.load("../models/system/system_vectorizer.pkl")

# Example logs (you can change these)
test_logs = [
    "PacketResponder <*> for block blk_<*> terminating",
    "ERROR failed to connect to database",
    "User root login failed from unknown IP",
]

# Transform
X_test = vectorizer.transform(test_logs)

# Predict
predictions = model.predict(X_test)

for log, pred in zip(test_logs, predictions):
    status = "ANOMALY 🚨" if pred == -1 else "NORMAL ✅"
    print(f"{log} → {status}")
