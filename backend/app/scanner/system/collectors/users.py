import psutil
from ..ssh_client import SSHClient


def collect_users(ssh=None):
    """
    Collect currently logged-in users
    Works for both local and remote scans
    """
    # Remote host
    if ssh:
        try:
            # Use 'who' command for remote user info
            who_output = ssh.execute("who")
            
            if who_output:
                user_list = []
                lines = who_output.strip().split('\n')
                
                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 5:
                            user_list.append({
                                "name": parts[0],
                                "terminal": parts[1],
                                "login_time": " ".join(parts[2:4]),
                                "host": parts[4] if len(parts) > 4 else "localhost"
                            })
                
                return user_list
            else:
                return []
                
        except Exception as e:
            print(f"Error collecting remote users: {e}")
            return {"error": str(e)}
    else:
        # Local host
        try:
            users = psutil.users()

            user_list = []
            for user in users:
                user_list.append({
                    "name": user.name,
                    "terminal": user.terminal,
                    "host": user.host,
                    "started": user.started
                })

            return user_list

        except Exception as e:
            return {"error": str(e)}


def detect_user_vulnerabilities(users, ssh=None):
    """
    Detect user-related security vulnerabilities
    """
    findings = []
    
    if not users or "error" in users:
        return findings
    
    # Check for suspicious user accounts
    suspicious_users = ["admin", "administrator", "root", "test", "guest", "demo"]
    
    for user in users:
        username = user.get("name", "").lower()
        
        if username in suspicious_users:
            findings.append({
                "type": "Suspicious User Account",
                "category": "A07: Identification and Authentication Failures",
                "severity": "MEDIUM",
                "url": "system",
                "confidence": "HIGH",
                "evidence": f"Suspicious user account detected: {username}",
                "exploits_available": []
            })
    
    # Check for users logged in from suspicious hosts
    if ssh and users:
        remote_hosts = set()
        for user in users:
            host = user.get("host", "")
            if host and host != "localhost" and "(" not in host:
                remote_hosts.add(host)
        
        if len(remote_hosts) > 5:  # Too many remote logins
            findings.append({
                "type": "Excessive Remote Logins",
                "category": "A04: Logging and Monitoring",
                "severity": "MEDIUM",
                "url": "system",
                "confidence": "MEDIUM",
                "evidence": f"Found logins from {len(remote_hosts)} different remote hosts",
                "exploits_available": []
            })
    
    return findings


def get_user_accounts(ssh=None):
    """
    Get all user accounts on the system (not just logged-in users)
    """
    user_accounts = []
    
    if ssh:
        try:
            # Get user accounts from /etc/passwd
            passwd_output = ssh.execute("cat /etc/passwd")
            
            if passwd_output:
                lines = passwd_output.strip().split('\n')
                
                for line in lines:
                    if line.strip() and not line.startswith("#"):
                        parts = line.split(":")
                        if len(parts) >= 7:
                            user_accounts.append({
                                "username": parts[0],
                                "uid": parts[2],
                                "gid": parts[3],
                                "home": parts[5],
                                "shell": parts[6]
                            })
        except Exception as e:
            print(f"Error getting user accounts: {e}")
    
    return user_accounts


def detect_user_account_vulnerabilities(user_accounts, ssh=None):
    """
    Detect vulnerabilities in user account configurations
    """
    findings = []
    
    if not user_accounts:
        return findings
    
    # Check for accounts with UID 0 (root-equivalent)
    root_accounts = [user for user in user_accounts if user.get("uid") == "0"]
    
    if len(root_accounts) > 1:  # More than just root
        findings.append({
            "type": "Multiple Root Accounts",
            "category": "A07: Identification and Authentication Failures",
            "severity": "HIGH",
            "url": "system",
            "confidence": "HIGH",
            "evidence": f"Found {len(root_accounts)} accounts with UID 0: {[u['username'] for u in root_accounts]}",
            "exploits_available": []
        })
    
    # Check for accounts with no password (shell is /bin/false or /usr/sbin/nologin)
    no_shell_accounts = [
        user for user in user_accounts 
        if user.get("shell") in ["/bin/false", "/usr/sbin/nologin", "/sbin/nologin"]
    ]
    
    # Check for accounts with empty password field (this would be in /etc/shadow typically)
    # For now, just check for suspicious patterns
    
    # Check for accounts with shell access that shouldn't have it
    privileged_shells = ["/bin/bash", "/bin/sh", "/bin/zsh", "/bin/csh"]
    system_accounts = ["daemon", "bin", "sys", "sync", "games", "man", "lp", "mail", "news", "uucp", "proxy", "www-data", "backup", "list", "irc", "gnats", "nobody", "systemd-network", "systemd-resolve", "syslog", "messagebus", "uuidd", "dnsmasq", "usbmux", "rtkit", "pulse", "speech-dispatcher", "avahi", "saned", "colord", "hplip", "geoclue", "gnome-initial-setup", "gdm"]
    
    shell_system_accounts = [
        user for user in user_accounts 
        if (user.get("username") in system_accounts and 
            user.get("shell") in privileged_shells)
    ]
    
    if shell_system_accounts:
        findings.append({
            "type": "System Accounts with Shell Access",
            "category": "A07: Identification and Authentication Failures",
            "severity": "MEDIUM",
            "url": "system",
            "confidence": "HIGH",
            "evidence": f"System accounts with shell access: {[u['username'] for u in shell_system_accounts]}",
            "exploits_available": []
        })
    
    return findings