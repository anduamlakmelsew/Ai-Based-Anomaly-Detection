from .providers import check_abuseipdb, check_virustotal


def check_ip_reputation(ip):

    results = []

    abuse_result = check_abuseipdb(ip)
    vt_result = check_virustotal(ip)

    results.append(abuse_result)
    results.append(vt_result)

    risk_score = calculate_threat_score(results)

    return {
        "ip": ip,
        "sources": results,
        "threat_score": risk_score
    }


def calculate_threat_score(results):

    score = 0

    for r in results:

        if r.get("source") == "abuseipdb":
            score += r.get("abuse_score", 0)

        if r.get("source") == "virustotal":
            score += r.get("malicious_reports", 0) * 10

    return min(score, 100)