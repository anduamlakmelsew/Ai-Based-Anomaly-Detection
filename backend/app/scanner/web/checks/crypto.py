import requests
import ssl
import socket
from urllib.parse import urlparse


# -----------------------------
# HTTPS Enforcement
# -----------------------------
def check_https_enforcement(url):
    findings = []

    if url.startswith("http://"):
        findings.append({
            "type": "Insecure Protocol (HTTP)",
            "category": "A02: Cryptographic Failure",
            "severity": "HIGH",
            "url": url,
            "confidence": "HIGH",
            "evidence": "Connection is not using HTTPS"
        })

    return findings


# -----------------------------
# TLS Certificate
# -----------------------------
def get_certificate(hostname):
    context = ssl.create_default_context()

    with socket.create_connection((hostname, 443), timeout=5) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            return ssock.getpeercert()


def check_certificate(url):
    findings = []
    parsed = urlparse(url)
    hostname = parsed.hostname

    try:
        cert = get_certificate(hostname)

        if not cert:
            return findings

        if "notAfter" in cert:
            findings.append({
                "type": "Certificate Info",
                "category": "A02: Cryptographic Failure",
                "severity": "INFO",
                "url": url,
                "confidence": "HIGH",
                "evidence": f"Certificate expires at {cert['notAfter']}"
            })

    except Exception as e:
        findings.append({
            "type": "TLS Connection Failure",
            "category": "A02: Cryptographic Failure",
            "severity": "MEDIUM",
            "url": url,
            "confidence": "MEDIUM",
            "evidence": str(e)
        })

    return findings


# -----------------------------
# TLS Version Check
# -----------------------------
def check_tls_version(hostname):
    findings = []

    context = ssl.SSLContext(ssl.PROTOCOL_TLS)

    try:
        with socket.create_connection((hostname, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                version = ssock.version()

                if version in ["TLSv1", "TLSv1.1"]:
                    findings.append({
                        "type": "Weak TLS Version",
                        "category": "A02: Cryptographic Failure",
                        "severity": "HIGH",
                        "confidence": "HIGH",
                        "evidence": f"Using deprecated TLS version: {version}"
                    })

    except Exception:
        pass

    return findings


# -----------------------------
# Cookie Security
# -----------------------------
def check_cookies(response, url):
    findings = []

    for cookie in response.cookies:
        if not cookie.secure:
            findings.append({
                "type": "Insecure Cookie",
                "category": "A02: Cryptographic Failure",
                "severity": "HIGH",
                "url": url,
                "confidence": "HIGH",
                "evidence": f"Cookie {cookie.name} missing Secure flag"
            })

        if not cookie.has_nonstandard_attr("HttpOnly"):
            findings.append({
                "type": "Cookie Missing HttpOnly",
                "category": "A02: Cryptographic Failure",
                "severity": "MEDIUM",
                "url": url,
                "confidence": "MEDIUM",
                "evidence": f"Cookie {cookie.name} missing HttpOnly flag"
            })

    return findings


# -----------------------------
# Sensitive Data Exposure
# -----------------------------
def check_sensitive_data(response, url):
    findings = []

    patterns = ["password", "secret", "api_key", "token"]

    body = response.text.lower()

    for p in patterns:
        if p in body:
            findings.append({
                "type": "Sensitive Data Exposure",
                "category": "A02: Cryptographic Failure",
                "severity": "HIGH",
                "url": url,
                "confidence": "LOW",
                "evidence": f"Potential sensitive keyword found: {p}"
            })

    return findings


# -----------------------------
# MAIN FUNCTION
# -----------------------------
def check_crypto(urls):
    findings = []

    headers = {
        "User-Agent": "Mozilla/5.0 (AI-Scanner/1.0)"
    }

    checked_hosts = set()

    for url in urls:
        parsed = urlparse(url)
        hostname = parsed.hostname

        # HTTPS enforcement
        findings += check_https_enforcement(url)

        # Request page
        try:
            res = requests.get(url, headers=headers, timeout=5)
        except Exception:
            continue

        # Cookie checks
        findings += check_cookies(res, url)

        # Sensitive data exposure
        findings += check_sensitive_data(res, url)

        # Certificate check
        findings += check_certificate(url)

        # TLS version check (avoid duplicate scans per host)
        if hostname and hostname not in checked_hosts:
            findings += check_tls_version(hostname)
            checked_hosts.add(hostname)

    return findings