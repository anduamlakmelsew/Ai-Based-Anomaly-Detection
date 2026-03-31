def compare_with_baseline(results):
    """
    Compare system scan results against baseline rules.
    """

    findings = []

    # Firewall check
    firewall = results.get("firewall")

    if firewall and not firewall.get("enabled"):
        findings.append({
            "type": "security_misconfiguration",
            "severity": "high",
            "message": "Firewall is disabled"
        })

    # Suspicious users
    users = results.get("users", [])

    if "root" in users:
        findings.append({
            "type": "privileged_account",
            "severity": "medium",
            "message": "Root account detected"
        })

    # Suspicious processes
    processes = results.get("processes", [])

    suspicious = ["nc", "netcat", "nmap"]

    for p in processes:
        if p in suspicious:
            findings.append({
                "type": "suspicious_process",
                "severity": "high",
                "message": f"Suspicious process running: {p}"
            })

    return findings