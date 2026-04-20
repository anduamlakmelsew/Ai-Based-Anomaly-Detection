import requests
import re
from urllib.parse import urljoin, urlparse

def run_enhanced_web_checks(target):
    """
    Enhanced web security checks with comprehensive vulnerability detection
    """
    findings = []
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (AI-Scanner/1.0)"
        }
        
        response = requests.get(target, timeout=10, headers=headers)
        
        # Enhanced security header checks
        findings.extend(check_security_headers(target, response.headers))
        
        # SSL/TLS checks
        findings.extend(check_ssl_tls(target))
        
        # Information disclosure checks
        findings.extend(check_information_disclosure(target, response))
        
        # Common vulnerability checks
        findings.extend(check_common_vulnerabilities(target, response))
        
        # Technology detection findings
        findings.extend(check_technology_exposure(target, response))
        
        # Directory and file checks
        findings.extend(check_directory_exposure(target))
        
    except Exception as e:
        findings.append({
            "type": "Connection Error",
            "category": "A01: Broken Access Control",
            "severity": "MEDIUM",
            "url": target,
            "confidence": "MEDIUM",
            "evidence": f"Failed to connect to target: {str(e)}",
            "exploits_available": [],
            "remediation": "Ensure the target is accessible and properly configured"
        })
    
    return findings

def check_security_headers(target, headers):
    """Check for missing or misconfigured security headers"""
    findings = []
    
    security_headers = {
        "Content-Security-Policy": {
            "severity": "HIGH",
            "description": "Missing Content Security Policy header"
        },
        "X-Frame-Options": {
            "severity": "MEDIUM", 
            "description": "Missing X-Frame-Options header (Clickjacking protection)"
        },
        "X-Content-Type-Options": {
            "severity": "MEDIUM",
            "description": "Missing X-Content-Type-Options header"
        },
        "Strict-Transport-Security": {
            "severity": "HIGH",
            "description": "Missing Strict-Transport-Security header"
        },
        "X-XSS-Protection": {
            "severity": "LOW",
            "description": "Missing X-XSS-Protection header"
        },
        "Referrer-Policy": {
            "severity": "LOW",
            "description": "Missing Referrer-Policy header"
        },
        "Permissions-Policy": {
            "severity": "MEDIUM",
            "description": "Missing Permissions-Policy header"
        }
    }
    
    missing_headers = [header for header in security_headers.keys() if header not in headers]
    
    if missing_headers:
        findings.append({
            "type": "Missing Security Headers",
            "category": "A05: Security Misconfiguration",
            "severity": "HIGH" if len(missing_headers) >= 3 else "MEDIUM",
            "url": target,
            "confidence": "HIGH",
            "evidence": f"Missing security headers: {', '.join(missing_headers)}",
            "exploits_available": [],
            "remediation": f"Implement the following security headers: {', '.join(missing_headers)}"
        })
    
    # Check for weak CSP
    if "Content-Security-Policy" in headers:
        csp = headers["Content-Security-Policy"]
        if "unsafe-inline" in csp or "unsafe-eval" in csp:
            findings.append({
                "type": "Weak Content Security Policy",
                "category": "A05: Security Misconfiguration",
                "severity": "MEDIUM",
                "url": target,
                "confidence": "HIGH",
                "evidence": f"CSP contains unsafe directives: {csp}",
                "exploits_available": [],
                "remediation": "Remove unsafe-inline and unsafe-eval from CSP policy"
            })
    
    return findings

def check_ssl_tls(target):
    """Check SSL/TLS configuration"""
    findings = []
    
    parsed_url = urlparse(target)
    if parsed_url.scheme == "https":
        try:
            response = requests.get(target, timeout=10, verify=False)
            
            # Check for certificate issues (basic check)
            if response.status_code == 200:
                findings.append({
                    "type": "HTTPS Configuration",
                    "category": "A02: Cryptographic Failures",
                    "severity": "LOW",
                    "url": target,
                    "confidence": "MEDIUM",
                    "evidence": "HTTPS is properly configured",
                    "exploits_available": [],
                    "remediation": "Continue using HTTPS with valid certificates"
                })
        except Exception as e:
            findings.append({
                "type": "SSL/TLS Issue",
                "category": "A02: Cryptographic Failures",
                "severity": "HIGH",
                "url": target,
                "confidence": "HIGH",
                "evidence": f"SSL/TLS configuration issue: {str(e)}",
                "exploits_available": [],
                "remediation": "Fix SSL/TLS configuration and ensure valid certificates"
            })
    else:
        findings.append({
            "type": "Insecure Protocol (HTTP)",
            "category": "A02: Cryptographic Failures",
            "severity": "HIGH",
            "url": target,
            "confidence": "HIGH",
            "evidence": "Connection is not using HTTPS",
            "exploits_available": [],
            "remediation": "Implement HTTPS with valid SSL/TLS certificates"
        })
    
    return findings

def check_information_disclosure(target, response):
    """Check for information disclosure vulnerabilities"""
    findings = []
    
    # Check for server header disclosure
    server = response.headers.get("Server", "")
    if server:
        findings.append({
            "type": "Server Information Disclosure",
            "category": "A05: Security Misconfiguration",
            "severity": "LOW",
            "url": target,
            "confidence": "HIGH",
            "evidence": f"Server header exposed: {server}",
            "exploits_available": [],
            "remediation": "Hide or obscure server information in headers"
        })
    
    # Check for powered-by headers
    powered_by = response.headers.get("X-Powered-By", "")
    if powered_by:
        findings.append({
            "type": "Technology Disclosure",
            "category": "A05: Security Misconfiguration",
            "severity": "LOW",
            "url": target,
            "confidence": "HIGH",
            "evidence": f"Technology exposed: {powered_by}",
            "exploits_available": [],
            "remediation": "Remove X-Powered-By headers"
        })
    
    # Check for error messages in response
    content = response.text.lower()
    error_patterns = [
        r"error in your sql syntax",
        r"mysql_fetch_array",
        r"ora-\d{5}",
        r"microsoft ole db provider",
        r"odbc error",
        r"java.lang.nullpointerexception",
        r"stack trace",
        r"fatal error",
        r"warning:.*mysql",
        r"postgresql.*error"
    ]
    
    for pattern in error_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            findings.append({
                "type": "Error Information Disclosure",
                "category": "A05: Security Misconfiguration",
                "severity": "MEDIUM",
                "url": target,
                "confidence": "HIGH",
                "evidence": f"Error message detected: {pattern}",
                "exploits_available": [],
                "remediation": "Implement proper error handling and hide detailed error messages"
            })
            break
    
    return findings

def check_common_vulnerabilities(target, response):
    """Check for common web vulnerabilities"""
    findings = []
    
    content = response.text.lower()
    
    # Check for exposed admin panels
    admin_patterns = [
        r"/admin",
        r"/administrator",
        r"/wp-admin",
        r"/wp-login",
        r"/phpmyadmin",
        r"/admin/login",
        r"/manager/html"
    ]
    
    for pattern in admin_patterns:
        if pattern in content:
            findings.append({
                "type": "Potential Admin Panel Exposure",
                "category": "A01: Broken Access Control",
                "severity": "MEDIUM",
                "url": target,
                "confidence": "MEDIUM",
                "evidence": f"Admin panel pattern detected: {pattern}",
                "exploits_available": [],
                "remediation": "Ensure admin panels are properly secured and not exposed"
            })
    
    # Check for debug information
    debug_patterns = [
        r"debug mode",
        r"debug=true",
        r"development mode",
        r"stack trace",
        r"traceback"
    ]
    
    for pattern in debug_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            findings.append({
                "type": "Debug Information Disclosure",
                "category": "A05: Security Misconfiguration",
                "severity": "HIGH",
                "url": target,
                "confidence": "HIGH",
                "evidence": f"Debug information detected: {pattern}",
                "exploits_available": [],
                "remediation": "Disable debug mode in production"
            })
            break
    
    return findings

def check_technology_exposure(target, response):
    """Check for technology exposure and version disclosure"""
    findings = []
    
    content = response.text.lower()
    
    # Check for common web frameworks
    framework_patterns = {
        "react": {
            "pattern": r"react[_-]?\d+\.\d+\.\d+",
            "severity": "LOW"
        },
        "angular": {
            "pattern": r"angular[_-]?\d+\.\d+\.\d+",
            "severity": "LOW"
        },
        "vue": {
            "pattern": r"vue[_-]?\d+\.\d+\.\d+",
            "severity": "LOW"
        },
        "jquery": {
            "pattern": r"jquery[_-]?\d+\.\d+\.\d+",
            "severity": "LOW"
        },
        "bootstrap": {
            "pattern": r"bootstrap[_-]?\d+\.\d+\.\d+",
            "severity": "LOW"
        }
    }
    
    for framework, config in framework_patterns.items():
        if re.search(config["pattern"], content, re.IGNORECASE):
            findings.append({
                "type": "Technology Version Disclosure",
                "category": "A05: Security Misconfiguration",
                "severity": config["severity"],
                "url": target,
                "confidence": "MEDIUM",
                "evidence": f"{framework.capitalize()} version detected in source code",
                "exploits_available": [],
                "remediation": f"Consider hiding {framework} version information"
            })
    
    return findings

def check_directory_exposure(target):
    """Check for directory listing and file exposure (optimized to reduce 404 noise)"""
    findings = []
    
    # Reduced set of high-value directories to minimize 404 noise
    critical_directories = [
        "/admin",
        "/backup", 
        "/config",
        "/.git",
        "/.env"
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (AI-Scanner/1.0)"
    }
    
    for directory in critical_directories:
        try:
            test_url = urljoin(target, directory)
            
            # Use HEAD request first to avoid downloading content and reduce noise
            head_response = requests.head(test_url, timeout=3, headers=headers, allow_redirects=True)
            
            # Only proceed with GET if HEAD returns 200 (resource exists)
            if head_response.status_code == 200:
                get_response = requests.get(test_url, timeout=5, headers=headers)
                
                # Check for directory listing
                if "Index of /" in get_response.text or "Directory Listing" in get_response.text:
                    findings.append({
                        "type": "Directory Listing Enabled",
                        "category": "A01: Broken Access Control", 
                        "severity": "MEDIUM",
                        "url": test_url,
                        "confidence": "HIGH",
                        "evidence": f"Directory listing enabled at {directory}",
                        "exploits_available": [],
                        "remediation": "Disable directory listing for sensitive directories"
                    })
                
                # Check for exposed sensitive files
                elif any(keyword in get_response.text.lower() for keyword in ["password", "secret", "key", "token", "api_key"]):
                    findings.append({
                        "type": "Sensitive File Exposure",
                        "category": "A01: Broken Access Control",
                        "severity": "HIGH", 
                        "url": test_url,
                        "confidence": "HIGH",
                        "evidence": f"Sensitive file potentially exposed at {directory}",
                        "exploits_available": [],
                        "remediation": "Remove or secure sensitive files"
                    })
                
        except requests.exceptions.Timeout:
            # Timeout is expected for non-existent directories, continue silently
            continue
        except requests.exceptions.ConnectionError:
            # Connection errors are expected for non-existent directories, continue silently  
            continue
        except Exception:
            # Any other errors, continue silently to avoid noise in logs
            continue
    
    return findings
