import pandas as pd
import os

BASE = "processed"

def inspect_parquet_folder(folder_path, name):
    print(f"\n📊 Inspecting {name} dataset...")

    try:
        files = [f for f in os.listdir(folder_path) if f.endswith(".parquet")]

        if not files:
            print("❌ No parquet files found")
            return

        file_path = os.path.join(folder_path, files[0])
        df = pd.read_parquet(file_path)

        print("Shape:", df.shape)
        print("Columns:", list(df.columns))

        print("\n🧾 Data Types:")
        print(df.dtypes)

        print("\n❗ Missing Values:")
        print(df.isnull().sum().sort_values(ascending=False).head(10))

        print("\n🔍 Sample:")
        print(df.head(3))

    except Exception as e:
        print("Error:", e)


def inspect_csv():
    print("\n📊 Inspecting Train/Test CSV...")

    try:
        X_train = pd.read_csv(os.path.join(BASE, "X_train.csv"))
        y_train = pd.read_csv(os.path.join(BASE, "y_train.csv"))

        print("X_train shape:", X_train.shape)
        print("y_train shape:", y_train.shape)

        print("\n🎯 Label Distribution:")
        print(y_train.value_counts())

    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    inspect_parquet_folder("processed/network_parquet", "NETWORK")
    inspect_parquet_folder("processed/web_parquet", "WEB")
    inspect_parquet_folder("processed/system_parquet", "SYSTEM")

    inspect_csv()
