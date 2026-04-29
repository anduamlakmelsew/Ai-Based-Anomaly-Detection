import pandas as pd
import os

# Base dataset path
BASE_PATH = "datasets"

# Files to inspec
files = {
    "CSIC2010": "web_csic2010/web_csic2010/CSIC2010.csv",
    "CSIC_DB_OWASP": "owasp_secdata/csic_database.csv",
    "XSS": "owasp_secdata/XSS_dataset.csv",
    "WAAD_CSIC": "web_anomalies_waad/csic_database.csv"
}

def inspect_dataset(name, path):
    full_path = os.path.join(BASE_PATH, path)
    
    print("\n" + "="*60)
    print(f"📂 DATASET: {name}")
    print("="*60)
    
    try:
        df = pd.read_csv(full_path, low_memory=False)
        
        print("\n🔹 Shape:", df.shape)
        print("\n🔹 Columns:")
        print(df.columns.tolist())
        
        print("\n🔹 Sample Data:")
        print(df.head(5))
        
        print("\n🔹 Info:")
        print(df.info())
        
        print("\n🔹 Missing Values:")
        print(df.isnull().sum())
        
    except Exception as e:
        print(f"❌ Error loading {name}: {e}")

# Run inspection
for name, path in files.items():
    inspect_dataset(name, path)
