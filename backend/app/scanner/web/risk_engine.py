def calculate_risk(findings):
    score = 0

    severity_weights = {
        "CRITICAL": 10,
        "HIGH": 7,
        "MEDIUM": 4,
        "LOW": 2,
        "INFO": 1
    }

    exploit_bonus = 5  # extra weight if exploit exists

    high_count = 0
    critical_count = 0
    exploitable_count = 0

    for f in findings:
        severity = f.get("severity", "LOW")
        base = severity_weights.get(severity, 1)

        score += base

        if severity == "HIGH":
            high_count += 1
        elif severity == "CRITICAL":
            critical_count += 1

        if f.get("exploits_available"):
            score += exploit_bonus
            exploitable_count += 1

    # Normalize score (0–100)
    max_possible = max(len(findings) * 10, 1)
    normalized_score = int((score / max_possible) * 100)

    # Determine level
    if normalized_score >= 80:
        level = "CRITICAL"
    elif normalized_score >= 60:
        level = "HIGH"
    elif normalized_score >= 40:
        level = "MEDIUM"
    else:
        level = "LOW"

    # Explanation generation
    explanation = []

    if critical_count > 0:
        explanation.append(f"{critical_count} critical issues detected")

    if high_count > 0:
        explanation.append(f"{high_count} high-risk vulnerabilities")

    if exploitable_count > 0:
        explanation.append(f"{exploitable_count} exploitable vulnerabilities")

    if not explanation:
        explanation.append("Low risk target with minimal exposure")

    return {
        "score": normalized_score,
        "level": level,
        "explanation": ", ".join(explanation)
    }