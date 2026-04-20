import psutil
from ..ssh_client import SSHClient


def get_running_processes(ssh=None):
    """
    Collect running processes (PID and name)
    Works for both local and remote scans
    """
    processes = []

    # Remote host
    if ssh:
        try:
            # Use ps command for remote processes
            ps_output = ssh.execute("ps aux")
            
            if ps_output:
                lines = ps_output.strip().split('\n')
                # Skip header line
                for line in lines[1:]:
                    if line.strip():
                        parts = line.split(None, 10)  # Split into max 11 parts
                        if len(parts) >= 11:
                            processes.append({
                                "user": parts[0],
                                "pid": parts[1],
                                "cpu": parts[2],
                                "mem": parts[3],
                                "vsz": parts[4],
                                "rss": parts[5],
                                "tty": parts[6],
                                "stat": parts[7],
                                "start": parts[8],
                                "time": parts[9],
                                "command": parts[10]
                            })
        except Exception as e:
            print(f"Error collecting remote processes: {e}")
            return {"error": str(e)}
    else:
        # Local host
        try:
            for proc in psutil.process_iter(attrs=["pid", "name", "username", "cpu_percent", "memory_percent"]):
                try:
                    processes.append({
                        "pid": proc.info["pid"],
                        "name": proc.info["name"],
                        "user": proc.info["username"],
                        "cpu": proc.info["cpu_percent"],
                        "mem": proc.info["memory_percent"]
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            print(f"Error collecting local processes: {e}")

    return processes


def detect_process_vulnerabilities(processes, ssh=None):
    """
    Detect suspicious or vulnerable processes
    """
    findings = []
    
    if not processes or "error" in processes:
        return findings
    
    # Common suspicious processes to check
    suspicious_processes = [
        "nc", "netcat", "ncat",           # Network tools
        "tcpdump", "wireshark", "tshark", # Packet capture
        "nmap", "masscan", "zenmap",      # Port scanners
        "john", "hashcat", "hydra",       # Password crackers
        "metasploit", "msfconsole",       # Exploitation tools
        "burpsuite", "sqlmap",            # Web testing tools
        "ettercap", "arpspoof",           # MITM tools
        "backdoor", "rootkit", "keylog"   # Malware indicators
    ]
    
    # Check for suspicious processes
    for proc in processes:
        command = proc.get("command", "").lower() if "command" in proc else proc.get("name", "").lower()
        
        for suspicious in suspicious_processes:
            if suspicious in command:
                findings.append({
                    "type": "Suspicious Process Detected",
                    "category": "A01: Broken Access Control",
                    "severity": "HIGH",
                    "url": "system",
                    "confidence": "HIGH",
                    "evidence": f"Suspicious process found: {command} (PID: {proc.get('pid', 'N/A')})",
                    "exploits_available": []
                })
                break
    
    # Check for processes running as root (if user info available)
    if ssh and processes:
        root_processes = [proc for proc in processes if proc.get("user") == "root"]
        
        if len(root_processes) > 10:  # Too many root processes
            findings.append({
                "type": "Excessive Root Processes",
                "category": "A05: Security Misconfiguration",
                "severity": "MEDIUM",
                "url": "system",
                "confidence": "MEDIUM",
                "evidence": f"Found {len(root_processes)} processes running as root user",
                "exploits_available": []
            })
    
    # Check for resource-intensive processes
    if ssh and processes:
        high_cpu_processes = []
        high_mem_processes = []
        
        for proc in processes:
            try:
                cpu = float(proc.get("cpu", 0))
                mem = float(proc.get("mem", 0))
                
                if cpu > 80:  # High CPU usage
                    high_cpu_processes.append(proc)
                if mem > 80:  # High memory usage
                    high_mem_processes.append(proc)
            except:
                continue
        
        if high_cpu_processes:
            findings.append({
                "type": "High CPU Usage Processes",
                "category": "A04: Logging and Monitoring",
                "severity": "LOW",
                "url": "system",
                "confidence": "MEDIUM",
                "evidence": f"Found {len(high_cpu_processes)} processes with >80% CPU usage",
                "exploits_available": []
            })
            
        if high_mem_processes:
            findings.append({
                "type": "High Memory Usage Processes", 
                "category": "A04: Logging and Monitoring",
                "severity": "LOW",
                "url": "system",
                "confidence": "MEDIUM",
                "evidence": f"Found {len(high_mem_processes)} processes with >80% memory usage",
                "exploits_available": []
            })
    
    return findings


def get_critical_processes(ssh=None):
    """
    Get list of critical system processes for monitoring
    """
    critical_processes = []
    
    if ssh:
        try:
            # Check for critical services
            critical_services = [
                "sshd", "systemd", "init", "cron", "crond",
                "rsyslog", "syslog-ng", "auditd",
                "firewalld", "iptables", "ufw"
            ]
            
            for service in critical_services:
                try:
                    # Check if service is running
                    result = ssh.execute(f"pgrep {service} 2>/dev/null")
                    if result and result.strip():
                        pids = result.strip().split('\n')
                        critical_processes.append({
                            "name": service,
                            "pids": pids,
                            "status": "running"
                        })
                except:
                    continue
        except Exception as e:
            print(f"Error getting critical processes: {e}")
    
    return critical_processes