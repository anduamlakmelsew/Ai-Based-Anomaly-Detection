import requests
from urllib.parse import urlparse

SENSITIVE_KEYWORDS = [
    "admin", "dashboard", "user", "account",
    "config", "settings", "api", "internal"
]


def is_sensitive(url):
    path = urlparse(url).path.lower()
    return any(keyword in path for keyword in SENSITIVE_KEYWORDS)


def check_access_control(urls):
    findings = []

    for url in urls:
        if not is_sensitive(url):
            continue

        try:
            # -----------------------------
            # 1. Unauthenticated Request
            # -----------------------------
            res = requests.get(
                url,
                timeout=5,
                allow_redirects=False,
                headers={"User-Agent": "AI-Scanner/1.0"}
            )

            body = res.text.lower()

            # -----------------------------
            # 2. Strong Detection (REAL ISSUE)
            # -----------------------------
            if res.status_code == 200:
                # Look for sensitive indicators in response
                if any(keyword in body for keyword in ["admin", "dashboard", "user", "config"]):
                    findings.append({
                        "type": "Broken Access Control",
                        "category": "A01: Broken Access Control",
                        "severity": "HIGH",
                        "url": url,
                        "confidence": "HIGH",
                        "evidence": f"Accessible sensitive endpoint with status 200. Response length: {len(res.text)}",
                        "exploits_available": []
                    })
                else:
                    # weaker signal
                    findings.append({
                        "type": "Potential Broken Access Control",
                        "category": "A01: Broken Access Control",
                        "severity": "MEDIUM",
                        "url": url,
                        "confidence": "MEDIUM",
                        "evidence": f"Endpoint returned 200 without authentication",
                        "exploits_available": []
                    })

            # -----------------------------
            # 3. Redirect Analysis
            # -----------------------------
            elif res.status_code in [301, 302]:
                location = res.headers.get("Location", "")

                if "login" not in location.lower():
                    findings.append({
                        "type": "Improper Access Control Redirect",
                        "category": "A01: Broken Access Control",
                        "severity": "MEDIUM",
                        "url": url,
                        "confidence": "LOW",
                        "evidence": f"Redirect without clear authentication enforcement → {location}",
                        "exploits_available": []
                    })

            # -----------------------------
            # 4. Forbidden but exposed
            # -----------------------------
            elif res.status_code == 403:
                findings.append({
                    "type": "Access Control Misconfiguration",
                    "category": "A01: Broken Access Control",
                    "severity": "LOW",
                    "url": url,
                    "confidence": "LOW",
                    "evidence": "Endpoint exists but returns 403 (possible misconfiguration)",
                    "exploits_available": []
                })

        except Exception:
            continue

    return findings