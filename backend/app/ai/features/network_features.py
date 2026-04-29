import pandas as pd

EXPECTED_FEATURES = 45


def build_network_features(scan_results):
    """
    Convert network scanner results into ML feature vector
    compatible with the UNSW trained model
    """

    features = {}

    # Basic network features
    features["open_ports"] = len(scan_results.get("open_ports", []))
    features["tcp_ports"] = len([p for p in scan_results.get("open_ports", []) if p == "tcp"])
    features["udp_ports"] = len([p for p in scan_results.get("open_ports", []) if p == "udp"])

    features["connections"] = scan_results.get("connections", 0)
    features["packets"] = scan_results.get("packets", 0)

    df = pd.DataFrame([features])

    # Pad missing columns to match model expectation
    current_features = df.shape[1]

    if current_features < EXPECTED_FEATURES:
        for i in range(EXPECTED_FEATURES - current_features):
            df[f"extra_feature_{i}"] = 0

    return df
