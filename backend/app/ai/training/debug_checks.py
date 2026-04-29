import pandas as pd

# Load data
X_train = pd.read_csv("processed/X_train.csv")
X_test = pd.read_csv("processed/X_test.csv")

# Check duplicates between train and test
duplicates = pd.merge(X_train, X_test, how='inner')
print("Duplicate rows:", len(duplicates))

# Show columns
print("\nColumns in dataset:")
print(X_train.columns)

# Feature importance (if model exists)
# (Optional - only if you load your trained model)
