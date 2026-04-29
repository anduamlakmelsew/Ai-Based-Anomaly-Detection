import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# Load data
X_train = pd.read_csv("processed/X_train.csv")
y_train = pd.read_csv("processed/y_train.csv").values.ravel()

# Train quick model
model = RandomForestClassifier(n_estimators=50, n_jobs=-1)
model.fit(X_train, y_train)

# Feature importance
importances = model.feature_importances_
features = X_train.columns

feat_imp = pd.DataFrame({
    "feature": features,
    "importance": importances
}).sort_values(by="importance", ascending=False)

print(feat_imp.head(10))
