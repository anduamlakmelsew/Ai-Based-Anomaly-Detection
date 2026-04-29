import pandas as pd
import re

# Load dataset
df = pd.read_parquet("processed/web_clean.parquet")

print("Loaded:", df.shape)

# 🔥 Feature extraction function
def extract_features(req):
    req = str(req).lower()

    return {
        "length": len(req),
        "num_digits": sum(c.isdigit() for c in req),
        "num_special": len(re.findall(r"[^\w\s]", req)),
        "num_params": req.count("="),
        "num_slashes": req.count("/"),
        "num_dots": req.count("."),

        # 🚨 Attack patterns
        "has_sql": int(any(x in req for x in ["select", "drop", "union", "insert"])),
        "has_xss": int("<script" in req or "javascript:" in req),
        "has_traversal": int("../" in req),
        "has_encoding": int("%" in req),
        "has_cmd": int(any(x in req for x in ["cmd=", "exec", "system("])),

        # HTTP method
        "is_post": int("post" in req),
        "is_get": int("get" in req),
    }

# Apply feature extraction
features = df["request"].apply(extract_features)

# Convert to dataframe
features_df = pd.DataFrame(list(features))

# Combine with label
final_df = pd.concat([features_df, df["label"]], axis=1)

print("Feature dataset shape:", final_df.shape)
print(final_df.head())

# Save
final_df.to_parquet("processed/web_features.parquet")

print("✅ Features extracted and saved!")
