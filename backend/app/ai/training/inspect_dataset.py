import pandas as pd

# Load dataset (folder of parquet files)
df = pd.read_parquet("processed/web_parquet")

print("\n✅ Dataset Loaded")
print("Shape:", df.shape)

# Columns
print("\n📊 Columns:")
print(df.columns.tolist())

# Data types
print("\n🧠 Data Types:")
print(df.dtypes)

# Missing values
print("\n⚠️ Missing Values:")
print(df.isnull().sum())

# Duplicate rows
print("\n🔁 Duplicates:", df.duplicated().sum())

# Target distribution (IMPORTANT)
if "label" in df.columns:
    print("\n🎯 Label Distribution:")
    print(df["label"].value_counts())
else:
    print("\n❌ No 'label' column found!")

# Sample data
print("\n🔍 Sample Data:")
print(df.head())
