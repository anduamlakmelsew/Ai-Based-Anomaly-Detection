import subprocess


def check_firewall(ssh=None):
    """
    Check firewall status.
    """

    try:

        if ssh:
            output = ssh.execute("sudo iptables -L")
        else:
            output = subprocess.getoutput("sudo iptables -L")

        enabled = "Chain" in output

        return {
            "enabled": enabled,
            "rules": output
        }

    except Exception:
        return {
            "enabled": False,
            "rules": ""
        }


def get_firewall_status(ssh=None):
    """
    Get comprehensive firewall status (alias for check_firewall)
    """
    return check_firewall(ssh)


def analyze_firewall_rules(ssh=None):
    """
    Analyze firewall rules for security issues
    """
    findings = []
    
    try:
        firewall_info = check_firewall(ssh)
        
        if firewall_info.get("enabled"):
            rules = firewall_info.get("rules", "")
            
            # Check for dangerous rules
            if "ACCEPT" in rules and "anywhere" in rules:
                findings.append({
                    "type": "Permissive Firewall Rules",
                    "category": "A05: Security Misconfiguration",
                    "severity": "MEDIUM",
                    "url": "system",
                    "confidence": "MEDIUM",
                    "evidence": "Firewall allows traffic from anywhere",
                    "exploits_available": []
                })
            
            # Check for default allow policy
            if "policy ACCEPT" in rules.lower():
                findings.append({
                    "type": "Default Allow Firewall Policy",
                    "category": "A05: Security Misconfiguration",
                    "severity": "HIGH",
                    "url": "system",
                    "confidence": "HIGH",
                    "evidence": "Firewall default policy is ACCEPT",
                    "exploits_available": []
                })
        else:
            findings.append({
                "type": "Firewall Disabled",
                "category": "A05: Security Misconfiguration",
                "severity": "HIGH",
                "url": "system",
                "confidence": "HIGH",
                "evidence": "Firewall is not enabled",
                "exploits_available": []
            })
    
    except Exception as e:
        print(f"Error analyzing firewall rules: {e}")
    
    return findings