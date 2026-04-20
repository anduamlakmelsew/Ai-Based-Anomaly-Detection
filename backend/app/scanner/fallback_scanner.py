import socket
import time
import re
from urllib.parse import urlparse
import requests
from datetime import datetime

def run_basic_port_scan(target):
    """
    Basic port scanner using Python socket without external dependencies
    """
    common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 8080, 8443]
    open_ports = []
    
    for port in common_ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((target, port))
            if result == 0:
                open_ports.append(port)
            sock.close()
        except:
            continue
    
    return open_ports

def detect_basic_services(target, open_ports):
    """
    Basic service detection based on port numbers
    """
    services = []
    port_service_map = {
        21: "FTP",
        22: "SSH", 
        23: "Telnet",
        25: "SMTP",
        53: "DNS",
        80: "HTTP",
        110: "POP3",
        143: "IMAP",
        443: "HTTPS",
        993: "IMAPS",
        995: "POP3S",
        8080: "HTTP-Alt",
        8443: "HTTPS-Alt"
    }
    
    for port in open_ports:
        service_name = port_service_map.get(port, "Unknown")
        services.append({
            "port": port,
            "protocol": "TCP",
            "state": "open",
            "service": service_name,
            "version": "Unknown"
        })
    
    return services

def run_basic_web_scan(target):
    """
    Basic web vulnerability scanner without external dependencies
    """
    findings = []
    
    # Ensure target has proper protocol
    if not target.startswith(('http://', 'https://')):
        target = 'http://' + target
    
    try:
        # Basic HTTP request
        response = requests.get(target, timeout=10, verify=False)
        
        # Check for security headers
        security_headers = [
            'Content-Security-Policy',
            'X-Frame-Options', 
            'X-XSS-Protection',
            'Strict-Transport-Security',
            'X-Content-Type-Options'
        ]
        
        missing_headers = []
        for header in security_headers:
            if header not in response.headers:
                missing_headers.append(header)
        
        if missing_headers:
            findings.append({
                "type": "Missing Security Headers",
                "severity": "MEDIUM",
                "description": f"Missing security headers: {', '.join(missing_headers)}",
                "evidence": f"Headers not found in response from {target}",
                "url": target,
                "remediation": "Add missing security headers to your web server configuration"
            })
        
        # Check for common vulnerabilities in response
        content = response.text.lower()
        
        # Check for exposed sensitive information
        sensitive_patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded Password"),
            (r'api[_-]?key\s*=\s*["\'][^"\']+["\']', "Hardcoded API Key"),
            (r'secret[_-]?key\s*=\s*["\'][^"\']+["\']', "Hardcoded Secret"),
        ]
        
        for pattern, vuln_type in sensitive_patterns:
            if re.search(pattern, content):
                findings.append({
                    "type": vuln_type,
                    "severity": "HIGH",
                    "description": f"Potential {vuln_type} found in page content",
                    "evidence": f"Pattern matched in {target}",
                    "url": target,
                    "remediation": "Remove hardcoded credentials from production code"
                })
        
        # Check for directory listing
        if 'index of /' in content.lower():
            findings.append({
                "type": "Directory Listing",
                "severity": "MEDIUM", 
                "description": "Directory listing is enabled",
                "evidence": f"Directory listing found at {target}",
                "url": target,
                "remediation": "Disable directory listing in web server configuration"
            })
            
    except requests.exceptions.RequestException as e:
        findings.append({
            "type": "Connection Error",
            "severity": "INFO",
            "description": f"Failed to connect to target: {str(e)}",
            "evidence": f"Connection failed for {target}",
            "url": target,
            "remediation": "Verify target is accessible and running"
        })
    
    return findings

def run_basic_system_scan(target):
    """
    Basic system information gathering (limited for security)
    """
    findings = []
    
    # Basic connectivity check
    try:
        # Try to resolve hostname
        ip = socket.gethostbyname(target)
        findings.append({
            "type": "Host Resolution",
            "severity": "INFO",
            "description": f"Target {target} resolves to IP {ip}",
            "evidence": f"DNS resolution successful",
            "target": target,
            "remediation": "Ensure DNS records are properly configured"
        })
        
        # Basic port scan
        open_ports = run_basic_port_scan(target)
        if open_ports:
            findings.append({
                "type": "Open Ports Detected",
                "severity": "LOW",
                "description": f"Found {len(open_ports)} open ports: {', '.join(map(str, open_ports))}",
                "evidence": f"Port scan results for {target}",
                "target": target,
                "remediation": "Review and close unnecessary ports"
            })
            
    except socket.gaierror:
        findings.append({
            "type": "DNS Resolution Failed",
            "severity": "HIGH",
            "description": f"Cannot resolve hostname: {target}",
            "evidence": f"DNS lookup failed for {target}",
            "target": target,
            "remediation": "Verify target hostname is correct"
        })
    
    return findings

def run_fallback_scan(target, scan_type):
    """
    Fallback scanner that works without external tools
    """
    print(f"🔄 Running fallback {scan_type} scan on {target}")
    
    result = {
        "target": target,
        "scan_type": scan_type,
        "timestamp": datetime.utcnow().isoformat(),
        "open_ports": [],
        "services": [],
        "findings": [],
        "risk": {"score": 0, "level": "LOW"},
        "success": True
    }
    
    try:
        if scan_type == "network":
            # Network scan
            open_ports = run_basic_port_scan(target)
            result["open_ports"] = open_ports
            result["services"] = detect_basic_services(target, open_ports)
            
            # Add findings
            if open_ports:
                result["findings"].append({
                    "type": "Network Services",
                    "severity": "LOW",
                    "description": f"Found {len(open_ports)} open ports",
                    "evidence": f"Ports: {', '.join(map(str, open_ports))}",
                    "target": target,
                    "remediation": "Review open ports for necessity"
                })
                
        elif scan_type == "web":
            # Web scan
            result["findings"] = run_basic_web_scan(target)
            
        elif scan_type == "system":
            # System scan  
            result["findings"] = run_basic_system_scan(target)
        
        # Calculate risk
        if result["findings"]:
            high_count = sum(1 for f in result["findings"] if f.get("severity") == "HIGH")
            medium_count = sum(1 for f in result["findings"] if f.get("severity") == "MEDIUM")
            low_count = sum(1 for f in result["findings"] if f.get("severity") == "LOW")
            
            risk_score = high_count * 10 + medium_count * 5 + low_count * 2
            
            if risk_score >= 20:
                risk_level = "HIGH"
            elif risk_score >= 10:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"
                
            result["risk"] = {
                "score": risk_score,
                "level": risk_level,
                "explanation": f"Risk calculated from {len(result['findings'])} findings"
            }
        
        print(f"✅ Fallback scan completed: {len(result['findings'])} findings")
        
    except Exception as e:
        print(f"❌ Fallback scan failed: {str(e)}")
        result["success"] = False
        result["error"] = str(e)
    
    return result
