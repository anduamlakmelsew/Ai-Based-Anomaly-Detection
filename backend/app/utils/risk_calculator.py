def calculate_network_risk(vulnerabilities):
    """
    Calculate overall network risk score.

    vulnerabilities = [
        {"severity": "high"},
        {"severity": "medium"},
        {"severity": "low"}
    ]
    """

    weights = {
        "critical": 10,
        "high": 7,
        "medium": 4,
        "low": 1
    }

    score = 0

    for vuln in vulnerabilities:

        severity = vuln.get("severity", "low").lower()

        score += weights.get(severity, 1)

    if score > 70:
        level = "Critical"
    elif score > 40:
        level = "High"
    elif score > 20:
        level = "Medium"
    else:
        level = "Low"

    return {
        "risk_score": score,
        "risk_level": level
    }