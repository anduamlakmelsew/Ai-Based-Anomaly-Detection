from .baseline_compare import compare_with_baseline


def calculate_system_risk(results):
    """
    Calculate system risk score.
    """

    findings = compare_with_baseline(results)

    score = 0

    severity_weights = {
        "low": 1,
        "medium": 3,
        "high": 6,
        "critical": 10
    }

    for finding in findings:
        severity = finding.get("severity", "low")
        score += severity_weights.get(severity, 1)

    return score, findings