import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler

def encode_features(df, label_column='label'):
    """
    Encode categorical columns and normalize numeric columns
    Returns X (features) and y (labels)
    """
    df = df.copy()
    # Remove IP address columns (not useful for ML)
    drop_cols = ["srcip", "dstip", "attack_cat"]
    df = df.drop(columns=[c for c in drop_cols if c in df.columns])

    # Identify categorical columns (object type)
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()

    # Remove label column if it's categorical
    if label_column in categorical_cols:
        categorical_cols.remove(label_column)

    print(f"Detected categorical columns: {categorical_cols}")

    # Encode categorical columns using LabelEncoder
    le_dict = {}
    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        le_dict[col] = le

    # Separate labels
    y = df[label_column] if label_column in df.columns else None

    # Drop label column from features
    X = df.drop(columns=[label_column]) if label_column in df.columns else df

    # Scale features
    scaler = StandardScaler()
    X_scaled = pd.DataFrame(
    scaler.fit_transform(X).astype("float32"),
    columns=X.columns 
)

    print("Feature encoding completed.")
    print("X shape:", X_scaled.shape)
    print("y shape:", y.shape if y is not None else None)

    return X_scaled, y, le_dict, scaler
