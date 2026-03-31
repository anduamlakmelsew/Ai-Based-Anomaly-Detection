from app.scanner.threat_intelligence.service import check_ip_reputation


def calculate_network_risk(scan_results):

    hosts = scan_results.get("hosts", [])

    findings = []
    total_risk_score = 0

    for host in hosts:

        ip = host.get("ip")
        open_ports = host.get("open_ports", [])

        host_risk = 0

        # Port-based risk
        for port in open_ports:

            if port in [21, 23, 3389]:   # risky services
                host_risk += 20

                findings.append({
                    "ip": ip,
                    "issue": f"Sensitive port open: {port}",
                    "severity": "high"
                })

        # Threat intelligence check
        intel = check_ip_reputation(ip)

        threat_score = intel.get("threat_score", 0)

        if threat_score > 50:

            findings.append({
                "ip": ip,
                "issue": "IP flagged by threat intelligence",
                "severity": "critical",
                "intel": intel
            })

            host_risk += threat_score

        total_risk_score += host_risk

        host["risk_score"] = host_risk
        host["threat_intel"] = intel

    return {
        "hosts": hosts,
        "findings": findings,
        "total_risk_score": total_risk_score
    }