import pandas as pd

# Load feature dataset
df = pd.read_parquet("processed/web_features.parquet")

print("Original shape:", df.shape)

# ----------------------------
# 1. Remove missing values
# ----------------------------
df = df.dropna()

# ----------------------------
# 2. Remove duplicates
# ----------------------------
df = df.drop_duplicates()

# ----------------------------
# 3. Fix data types
# ----------------------------
df["label"] = df["label"].astype(int)

# Convert all feature columns to numeric (safety)
feature_cols = df.columns.drop("label")
df[feature_cols] = df[feature_cols].apply(pd.to_numeric, errors="coerce")

# Drop again if coercion introduced NaNs
df = df.dropna()

# ----------------------------
# 4. Reset index
# ----------------------------
df = df.reset_index(drop=True)

print("Cleaned shape:", df.shape)

# ----------------------------
# 5. Class distribution check
# ----------------------------
print("\nLabel distribution:")
print(df["label"].value_counts())

# ----------------------------
# 6. Save cleaned dataset
# ----------------------------
df.to_parquet("processed/web_features_clean.parquet")

print("\n✅ Clean dataset saved: processed/web_features_clean.parquet")
