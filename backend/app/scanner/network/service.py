from .service_detection import detect_services
from .vulnerability import scan_vulnerabilities


def calculate_risk(vulnerabilities):
    score = 0

    weights = {
        "CRITICAL": 10,
        "HIGH": 7,
        "MEDIUM": 4,
        "LOW": 2,
        "INFO": 1
    }

    for v in vulnerabilities:
        severity = v.get("severity", "INFO").upper()
        score += weights.get(severity, 1)

    if score > 20:
        level = "HIGH"
    elif score > 10:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {
        "score": score,
        "level": level
    }


def run_network_scan(target):
    try:
        # -----------------------------
        # 1. Detect services
        # -----------------------------
        result = detect_services(target)

        if not result.get("success"):
            return {
                "target": target,
                "vulnerabilities": [],
                "findings": [],
                "total_urls": 0,
                "total_urls_scanned": 0,
                "risk": {
                    "score": 0,
                    "level": "LOW"
                },
                "error": result.get("error")
            }

        services = result.get("services", [])

        # -----------------------------
        # 2. Vulnerability scan
        # -----------------------------
        vulnerabilities = scan_vulnerabilities(services)

        # -----------------------------
        # 3. Normalize vulnerabilities
        # -----------------------------
        normalized = []
        for v in vulnerabilities:
            normalized.append({
                "type": v.get("type", "Network Issue"),
                "category": v.get("category", "Network"),
                "severity": v.get("severity", "LOW").upper(),
                "url": target,
                "confidence": v.get("confidence", "MEDIUM"),
                "evidence": v.get("evidence", ""),
                "exploits_available": v.get("exploits_available", [])
            })

        # -----------------------------
        # 4. Risk scoring
        # -----------------------------
        risk = calculate_risk(normalized)

        # -----------------------------
        # 5. Final Output (UNIFIED)
        # -----------------------------
        return {
            "target": target,

            "services": services,

            # ✅ unified
            "vulnerabilities": normalized,
            "findings": normalized,

            "total_urls": 0,
            "total_urls_scanned": 0,

            "risk": risk
        }

    except Exception as e:
        return {
            "target": target,
            "vulnerabilities": [],
            "findings": [],
            "total_urls": 0,
            "total_urls_scanned": 0,
            "risk": {
                "score": 0,
                "level": "LOW"
            },
            "error": str(e)
        }