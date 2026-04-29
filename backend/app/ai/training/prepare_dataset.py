import pandas as pd
import os

# Correct UNSW-NB15 column names
unsw_columns = [
    "srcip","sport","dstip","dsport","proto","state","dur",
    "sbytes","dbytes","sttl","dttl","sloss","dloss","service",
    "Sload","Dload","Spkts","Dpkts","swin","dwin","stcpb","dtcpb",
    "smeansz","dmeansz","trans_depth","res_bdy_len",
    "Sjit","Djit","Stime","Ltime","Sintpkt","Dintpkt",
    "tcprtt","synack","ackdat","is_sm_ips_ports",
    "ct_state_ttl","ct_flw_http_mthd","is_ftp_login",
    "ct_ftp_cmd","ct_srv_src","ct_srv_dst","ct_dst_ltm",
    "ct_src_ltm","ct_src_dport_ltm","ct_dst_sport_ltm",
    "ct_dst_src_ltm","attack_cat","label"
]

# -----------------------------
# Load ALL UNSW parts
# -----------------------------
dataset_path = "datasets/network_data_unsw/"

files = [
    "UNSW-NB15_1.csv",
    "UNSW-NB15_2.csv",
    "UNSW-NB15_3.csv",
    "UNSW-NB15_4.csv"
]

df_list = []

for file in files:
    file_path = os.path.join(dataset_path, file)
    print(f"Loading {file}...")
    temp_df = pd.read_csv(
        file_path,
        names=unsw_columns,
        low_memory=False
    )
    df_list.append(temp_df)

# Combine all files
df = pd.concat(df_list, ignore_index=True)

print("\n✅ All parts combined.")
print("Dataset shape:", df.shape)
print("\nLabel distribution:\n", df["label"].value_counts())
# -----------------------------
# Drop attack category
# -----------------------------
df = df.drop(columns=["attack_cat"])

# -----------------------------
# Encode categorical columns (Memory Efficient)
# -----------------------------
from sklearn.preprocessing import LabelEncoder

categorical_cols = df.select_dtypes(include=["object"]).columns
print("\nCategorical columns:", categorical_cols)

le = LabelEncoder()

for col in categorical_cols:
    df[col] = le.fit_transform(df[col].astype(str))

print("Encoding complete.")

# -----------------------------
# Reduce memory usage
# -----------------------------
print("\nOptimizing memory usage...")

for col in df.columns:
    if df[col].dtype == "int64":
        df[col] = df[col].astype("int32")
    elif df[col].dtype == "float64":
        df[col] = df[col].astype("float32")

print("Memory optimization complete.")

# -----------------------------
# Sample dataset (IMPORTANT for 6GB RAM)
# -----------------------------
print("\nSampling dataset for safe training...")

# Take 500,000 rows total (balanced)
normal_df = df[df["label"] == 0].sample(250000, random_state=42)
attack_df = df[df["label"] == 1].sample(250000, random_state=42)

df_sampled = pd.concat([normal_df, attack_df])

print("Sampled dataset shape:", df_sampled.shape)

df = df_sampled

from sklearn.model_selection import train_test_split

X = df.drop("label", axis=1)
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("\nTraining set:", X_train.shape)
print("Test set:", X_test.shape)
# -----------------------------
# Save processed dataset
# -----------------------------
import os

print("\nSaving processed dataset...")

os.makedirs("processed", exist_ok=True)

X_train.to_csv("processed/X_train.csv", index=False)
X_test.to_csv("processed/X_test.csv", index=False)
y_train.to_csv("processed/y_train.csv", index=False)
y_test.to_csv("processed/y_test.csv", index=False)

print("✅ Dataset preprocessing complete and saved.")