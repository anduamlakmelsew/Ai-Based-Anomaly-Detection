import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

# Load data
X_train = pd.read_csv("processed/X_train.csv")
y_train = pd.read_csv("processed/y_train.csv").values.ravel()

X_test = pd.read_csv("processed/X_test.csv")
y_test = pd.read_csv("processed/y_test.csv").values.ravel()

print("Data loaded:")
print(X_train.shape, X_test.shape)

# Train model
model = RandomForestClassifier(n_estimators=100, n_jobs=-1)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))
