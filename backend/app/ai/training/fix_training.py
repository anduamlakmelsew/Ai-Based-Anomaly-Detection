import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

# -------------------------
# 1. Load dataset
# -------------------------
df = pd.read_csv("processed/X_train.csv")
y = pd.read_csv("processed/y_train.csv").values.ravel()

print("Original shape:", df.shape)

# -------------------------
# 2. Remove leakage features
# -------------------------
leak_columns = [
    'srcip', 'dstip', 'sport', 'dsport'
]

df = df.drop(columns=[col for col in leak_columns if col in df.columns])

# -------------------------
# 3. Remove duplicates
# -------------------------
df["label"] = y
df = df.drop_duplicates()

print("After removing duplicates:", df.shape)

# Separate again
X = df.drop(columns=["label"])
y = df["label"]

# -------------------------
# 4. Encode categorical features
# -------------------------
X = pd.get_dummies(X)

# -------------------------
# 5. Train/Test Split (IMPORTANT)
# -------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("Train size:", X_train.shape)
print("Test size:", X_test.shape)

# -------------------------
# 6. Train model
# -------------------------
model = RandomForestClassifier(
    n_estimators=100,
    n_jobs=-1,
    random_state=42
)

model.fit(X_train, y_train)

# -------------------------
# 7. Evaluate
# -------------------------
y_pred = model.predict(X_test)

print("\nClassification Report:\n")
print(classification_report(y_test, y_pred))
