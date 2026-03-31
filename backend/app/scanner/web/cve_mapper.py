from app.scanner.vulnerability_intelligence.cve_matcher import match_cves
from app.scanner.vulnerability_intelligence.exploit_checker import check_exploit
from app.scanner.vulnerability_intelligence.remediation import generate_remediation


def enrich_findings(findings):
    enriched = []

    for finding in findings:
        try:
            # 🔍 Match CVEs based on type/keywords
            cves = match_cves(finding)

            # 💣 Check if exploit exists
            exploits = []
            for cve in cves:
                if check_exploit(cve):
                    exploits.append(cve)

            # 🛠 Generate remediation
            remediation = generate_remediation(finding)

            # 📦 Combine everything
            enriched.append({
                **finding,
                "cves": cves,
                "exploits_available": exploits,
                "remediation": remediation
            })

        except Exception as e:
            enriched.append({
                **finding,
                "error": str(e)
            })

    return enriched