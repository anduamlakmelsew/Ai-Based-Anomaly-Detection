import requests
from .injection import run_injection_tests
from .crawler import crawl
from .enhanced_web_checks import run_enhanced_web_checks

# OWASP Checks
from .checks.access_control import check_access_control
from .checks.idor import check_idor
from .checks.authentication import check_authentication
from .checks.crypto import check_crypto

# Intelligence + Risk
from .cve_mapper import enrich_findings
from .risk_engine import calculate_risk


def run_web_scan(target, mode="active"):
    findings = []

    headers = {
        "User-Agent": "Mozilla/5.0 (AI-Scanner/1.0)"
    }

    # -----------------------------
    # 1. Initial Request
    # -----------------------------
    try:
        r = requests.get(target, headers=headers, timeout=5)
    except Exception as e:
        return {
            "target": target,
            "vulnerabilities": [],
            "findings": [],
            "total_urls": 0,
            "total_urls_scanned": 0,
            "risk": {
                "score": 0,
                "level": "LOW",
                "explanation": "Target unreachable"
            },
            "error": str(e)
        }

    # -----------------------------
    # 2. Security Header Check
    # -----------------------------
    required_headers = [
        "Content-Security-Policy",
        "X-Frame-Options",
        "Strict-Transport-Security"
    ]

    missing = [h for h in required_headers if h not in r.headers]

    if missing:
        findings.append({
            "type": "Missing Security Headers",
            "category": "A05: Security Misconfiguration",
            "severity": "MEDIUM",
            "url": target,
            "confidence": "HIGH",
            "evidence": f"Missing headers: {', '.join(missing)}",
            "exploits_available": []  # ✅ REQUIRED
        })

    # -----------------------------
    # 3. Crawl Target
    # -----------------------------
    try:
        urls = crawl(target)
        if not urls:
            urls = [target]
    except Exception:
        urls = [target]

    # -----------------------------
    # 4. Enhanced Security Scanning
    # -----------------------------
    
    if mode in ["active", "internal"]:
        findings += check_access_control(urls)
        findings += check_idor(urls)
        findings += check_authentication(urls)
        findings += check_crypto(urls)
        
        # Enhanced web security checks
        enhanced_findings = run_enhanced_web_checks(target)
        findings.extend(enhanced_findings)
        
        # Injection tests (🔥 VERY IMPORTANT)
        for url in urls:
            findings += run_injection_tests(url)
    

    # -----------------------------
    # 5. Normalize findings (IMPORTANT)
    # -----------------------------
    normalized = []
    for f in findings:
        normalized.append({
            "type": f.get("type", "Unknown"),
            "category": f.get("category", "General"),
            "severity": f.get("severity", "LOW").upper(),
            "url": f.get("url", target),
            "confidence": f.get("confidence", "MEDIUM"),
            "evidence": f.get("evidence", ""),
            "exploits_available": f.get("exploits_available", [])
        })

    # -----------------------------
    # 6. CVE Enrichment
    # -----------------------------
    enriched_findings = enrich_findings(normalized)

    # -----------------------------
    # 7. Risk Scoring
    # -----------------------------
    risk_summary = calculate_risk(enriched_findings)

    # -----------------------------
    # 8. Final Output (UNIFIED)
    # -----------------------------
    return {
        "target": target,
        "mode": mode,

        # ✅ CORE FOR PIPELINE
        "vulnerabilities": enriched_findings,
        "findings": enriched_findings,

        "total_urls": len(urls),
        "total_urls_scanned": len(urls),

        "risk": risk_summary
    }