import joblib
import os

from ai.features.network_features import build_network_features

# Path to trained model
MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "../models/network/unsw_rf_model.joblib"
)

print("Loading AI network model...")
model = joblib.load(MODEL_PATH)
print("AI model loaded.")


def analyze_network(scan_results):
    """
    Run AI intrusion detection on network scan results
    """

    # Convert scan output to ML features
    features = build_network_features(scan_results)

    # Run prediction
    prediction = model.predict(features)[0]

    if prediction == 1:
        result = {
            "status": "attack",
            "message": "⚠️ Potential network intrusion detected"
        }
    else:
        result = {
            "status": "normal",
            "message": "✅ Network traffic appears normal"
        }

    return result


# Optional test
if __name__ == "__main__":

    test_scan = {
        "open_ports": [22, 80, 443],
        "connections": 150,
        "packets": 1200
    }

    result = analyze_network(test_scan)

    print("\nAI Analysis Result:")
    print(result)

