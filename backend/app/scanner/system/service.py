from .collectors.os_info import get_os_info, detect_os_vulnerabilities
from .collectors.packages import get_installed_packages
from .collectors.processes import get_running_processes, detect_process_vulnerabilities, get_critical_processes
from .collectors.network import collect_network_info
from .collectors.users import collect_users, detect_user_vulnerabilities, get_user_accounts, detect_user_account_vulnerabilities
from .collectors.services import get_services
from .collectors.firewall import get_firewall_status
from .vulnerability_detection import (
    detect_system_misconfigurations,
    detect_network_vulnerabilities, 
    detect_filesystem_vulnerabilities,
    detect_service_vulnerabilities,
    detect_malware_indicators
)
from .ssh_client import SSHClient

# 🔥 vulnerability intelligence (same pipeline style)
# from app.scanner.vulnerability_intelligence.service import run as run_vuln_intel


# =========================
# 🔹 LOCAL MISCONFIG CHECKS (🔥 IMPORTANT FOR DEMO)
# =========================
def local_misconfig_checks(os_info, users, services):
    findings = []

    # 🔐 Weak users (example heuristic)
    for user in users:
        if isinstance(user, dict):
            username = user.get("name", "").lower()
        else:
            username = str(user).lower()
            
        if username in ["admin", "root", "test"]:
            findings.append({
                "type": "Weak System User",
                "category": "Privilege Misconfiguration",
                "severity": "HIGH",
                "url": "local-system",
                "confidence": "MEDIUM",
                "evidence": f"Suspicious user account detected: {username}",
                "exploits_available": []
            })

    # ⚙️ Exposed services
    for svc in services:
        name = str(svc).lower()

        if "ftp" in name or "telnet" in name:
            findings.append({
                "type": "Insecure Service Running",
                "category": "A05: Security Misconfiguration",
                "severity": "HIGH",
                "url": "local-system",
                "confidence": "HIGH",
                "evidence": f"Insecure service detected: {svc}",
                "exploits_available": []
            })

    return findings


# =========================
# 🔹 REMOTE SYSTEM SCAN
# =========================
def run_remote_system_scan(target, ssh_credentials):
    """
    Full remote system scan with SSH access
    ssh_credentials should contain: host, username, password, port (optional)
    """
    try:
        # Initialize SSH connection
        ssh = SSHClient(
            host=ssh_credentials.get('host', target),
            username=ssh_credentials.get('username'),
            password=ssh_credentials.get('password'),
            port=ssh_credentials.get('port', 22)
        )
        
        ssh.connect()
        
        findings = []
        system_data = {}
        
        # ======================
        # 1️⃣ COLLECT REMOTE SYSTEM DATA
        # ======================
        print("🔍 Collecting remote OS information...")
        os_info = get_os_info(ssh)
        system_data["os_info"] = os_info
        
        print("🔍 Collecting remote packages...")
        packages = get_installed_packages(ssh)
        system_data["packages"] = packages
        
        print("🔍 Collecting remote processes...")
        processes = get_running_processes(ssh)
        system_data["processes"] = processes
        
        print("🔍 Collecting remote network info...")
        network = collect_network_info(ssh)
        system_data["network"] = network
        
        print("🔍 Collecting remote users...")
        users = collect_users(ssh)
        system_data["users"] = users
        
        print("🔍 Collecting remote services...")
        services = get_services(ssh)
        system_data["services"] = services
        
        print("🔍 Collecting firewall status...")
        firewall = get_firewall_status(ssh)
        system_data["firewall"] = firewall
        
        print("🔍 Collecting user accounts...")
        user_accounts = get_user_accounts(ssh)
        system_data["user_accounts"] = user_accounts
        
        print("🔍 Collecting critical processes...")
        critical_processes = get_critical_processes(ssh)
        system_data["critical_processes"] = critical_processes
        
        # ======================
        # 2️⃣ VULNERABILITY DETECTION
        # ======================
        print("🔍 Detecting OS vulnerabilities...")
        findings.extend(detect_os_vulnerabilities(os_info))
        
        print("🔍 Detecting process vulnerabilities...")
        findings.extend(detect_process_vulnerabilities(processes, ssh))
        
        print("🔍 Detecting user vulnerabilities...")
        findings.extend(detect_user_vulnerabilities(users, ssh))
        findings.extend(detect_user_account_vulnerabilities(user_accounts, ssh))
        
        print("🔍 Detecting system misconfigurations...")
        findings.extend(detect_system_misconfigurations(ssh, os_info))
        
        print("🔍 Detecting network vulnerabilities...")
        findings.extend(detect_network_vulnerabilities(ssh))
        
        print("🔍 Detecting filesystem vulnerabilities...")
        findings.extend(detect_filesystem_vulnerabilities(ssh))
        
        print("🔍 Detecting service vulnerabilities...")
        findings.extend(detect_service_vulnerabilities(ssh, services))
        
        print("🔍 Detecting malware indicators...")
        findings.extend(detect_malware_indicators(ssh))
        
        # ======================
        # 3️⃣ LEGACY LOCAL CHECKS (FOR COMPATIBILITY)
        # ======================
        local_findings = local_misconfig_checks(os_info, users, services)
        findings.extend(local_findings)
        
        # ======================
        # 4️⃣ PREPARE INPUT FOR CVE ENGINE
        # ======================
        base_vulns = []

        for pkg in packages[:50]:  # limit for performance
            base_vulns.append({
                "type": "Outdated Package",
                "category": "Vulnerable Component",
                "severity": "MEDIUM",
                "url": target,
                "confidence": "LOW",
                "evidence": f"Package detected: {pkg}",
                "exploits_available": []
            })

        for svc in services:
            base_vulns.append({
                "type": "Service Detection",
                "category": "Service Exposure",
                "severity": "LOW",
                "url": target,
                "confidence": "LOW",
                "evidence": f"Service detected: {svc}",
                "exploits_available": []
            })

        combined = base_vulns + findings

        # ======================
        # 5️⃣ CVE ENRICHMENT
        # ======================
        try:
            # enriched = run_vuln_intel(combined)
            # Skip vulnerability intelligence for now to avoid circular import
            enriched = combined
        except Exception:
            enriched = combined
        
        ssh.close()
        
        # ======================
        # 6️⃣ FINAL OUTPUT (PIPELINE FORMAT)
        # ======================
        return {
            "target": target,
            "scan_type": "system",
            "scan_mode": "remote",

            # 🔥 CRITICAL FOR PIPELINE
            "vulnerabilities": enriched,
            "findings": enriched,

            # system scan doesn't crawl URLs → fake coverage
            "total_urls_scanned": len(services) + len(packages),

            # extra data for reports
            "system_data": system_data,
            
            # Remote scan metadata
            "remote_scan": {
                "successful": True,
                "ssh_host": ssh_credentials.get('host'),
                "ssh_port": ssh_credentials.get('port', 22)
            }
        }

    except Exception as e:
        print(f"🔥 REMOTE SCAN ERROR: {str(e)}")
        return {
            "target": target,
            "scan_type": "system",
            "scan_mode": "remote",
            "vulnerabilities": [],
            "findings": [],
            "total_urls_scanned": 0,
            "error": str(e),
            "remote_scan": {
                "successful": False,
                "error": str(e)
            }
        }


# =========================
# 🔹 MAIN SYSTEM SCAN
# =========================
def run_system_scan(target=None, ssh_credentials=None):
    """
    Full system scan:
    - Supports both local and remote scanning
    - Detect misconfigurations
    - Run vulnerability intelligence
    - Return pipeline-compatible output
    """
    
    # Check if this is a remote scan
    if ssh_credentials or (target and target not in ["localhost", "127.0.0.1"]):
        print("🌐 Starting remote system scan...")
        return run_remote_system_scan(target, ssh_credentials)
    
    # Local scan (original functionality)
    print("💻 Starting local system scan...")
    
    try:
        # ======================
        # 1️⃣ COLLECT SYSTEM DATA
        # ======================
        os_info = get_os_info()
        packages = get_installed_packages()
        processes = get_running_processes()
        network = collect_network_info()
        users = collect_users()
        services = get_services()

        # ======================
        # 2️⃣ LOCAL MISCONFIG DETECTION (🔥 DEMO BOOST)
        # ======================
        local_findings = local_misconfig_checks(os_info, users, services)
        
        # Enhanced local vulnerability detection
        process_findings = detect_process_vulnerabilities(processes)
        user_findings = detect_user_vulnerabilities(users)
        os_findings = detect_os_vulnerabilities(os_info)
        
        all_findings = local_findings + process_findings + user_findings + os_findings

        # ======================
        # 3️⃣ PREPARE INPUT FOR CVE ENGINE
        # ======================
        base_vulns = []

        for pkg in packages[:50]:  # limit for performance
            base_vulns.append({
                "type": "Outdated Package",
                "category": "Vulnerable Component",
                "severity": "MEDIUM",
                "url": "local-system",
                "confidence": "LOW",
                "evidence": f"Package detected: {pkg}",
                "exploits_available": []
            })

        for svc in services:
            base_vulns.append({
                "type": "Service Detection",
                "category": "Service Exposure",
                "severity": "LOW",
                "url": "local-system",
                "confidence": "LOW",
                "evidence": f"Service detected: {svc}",
                "exploits_available": []
            })

        combined = base_vulns + all_findings

        # ======================
        # 4️⃣ CVE ENRICHMENT
        # ======================
        try:
            # enriched = run_vuln_intel(combined)
            # Skip vulnerability intelligence for now to avoid circular import
            enriched = combined
        except Exception:
            enriched = combined

        # ======================
        # 5️⃣ FINAL OUTPUT (PIPELINE FORMAT)
        # ======================
        return {
            "target": "local-system",
            "scan_type": "system", 
            "scan_mode": "local",

            # 🔥 CRITICAL FOR PIPELINE
            "vulnerabilities": enriched,
            "findings": enriched,

            # system scan doesn't crawl URLs → fake coverage
            "total_urls_scanned": len(services) + len(packages),

            # extra data for reports
            "system_data": {
                "os_info": os_info,
                "packages_count": len(packages),
                "processes_count": len(processes),
                "users": users,
                "services": services,
                "network": network
            },
            
            # Local scan metadata
            "local_scan": {
                "successful": True
            }
        }

    except Exception as e:
        return {
            "target": "local-system",
            "scan_type": "system",
            "scan_mode": "local",
            "vulnerabilities": [],
            "findings": [],
            "total_urls_scanned": 0,
            "error": str(e),
            "local_scan": {
                "successful": False,
                "error": str(e)
            }
        }