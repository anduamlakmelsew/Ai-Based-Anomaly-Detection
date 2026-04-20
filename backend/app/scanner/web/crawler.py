import requests
from bs4 import BeautifulSoup


def crawl(target):
    """Simple crawler that returns URLs found on the target"""
    urls = []
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (AI-Scanner/1.0)"
        }
        
        response = requests.get(target, timeout=10, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract links
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if href.startswith("http"):
                urls.append(href)
            elif href.startswith("/"):
                # Convert relative URLs to absolute
                from urllib.parse import urljoin
                urls.append(urljoin(target, href))
        
        # Remove duplicates and limit
        urls = list(set(urls))[:50]
        
    except Exception as e:
        print(f"Crawler error: {e}")
        # Return the target URL as fallback
        urls = [target]
    
    return urls


def run_web_scan(target):
    findings = []

    result = {
        "target": target,
        "status_code": None,
        "title": "",
        "links": [],
        "technologies": [],
        "keywords": []
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (AI-Scanner/1.0)"
    }

    try:
        response = requests.get(target, timeout=10, headers=headers)
        result["status_code"] = response.status_code

        soup = BeautifulSoup(response.text, "html.parser")

        # =========================
        # 🧾 TITLE
        # =========================
        if soup.title and soup.title.string:
            result["title"] = soup.title.string.strip()
            result["keywords"].append(result["title"].lower())

        # =========================
        # 🔗 LINKS
        # =========================
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if href.startswith("http"):
                result["links"].append(href)

        # =========================
        # 🧠 META KEYWORDS
        # =========================
        for meta in soup.find_all("meta"):
            content = meta.get("content")
            if content:
                result["keywords"].append(content.lower())

        # =========================
        # ⚙️ TECHNOLOGY DETECTION
        # =========================
        for script in soup.find_all("script", src=True):
            src = script["src"].lower()

            if "react" in src:
                result["technologies"].append("React")
            elif "angular" in src:
                result["technologies"].append("Angular")
            elif "vue" in src:
                result["technologies"].append("Vue")

        # =========================
        # 🔐 SECURITY HEADER CHECK
        # =========================
        required_headers = [
            "Content-Security-Policy",
            "X-Frame-Options",
            "Strict-Transport-Security"
        ]

        missing = [h for h in required_headers if h not in response.headers]

        if missing:
            findings.append({
                "type": "Missing Security Headers",
                "category": "A05: Security Misconfiguration",
                "severity": "MEDIUM",
                "url": target,
                "confidence": "HIGH",
                "evidence": f"Missing headers: {', '.join(missing)}",
                "exploits_available": []
            })

        # =========================
        # 🧠 TECHNOLOGY DISCLOSURE
        # =========================
        if result["technologies"]:
            findings.append({
                "type": "Technology Disclosure",
                "category": "Information Disclosure",
                "severity": "LOW",
                "url": target,
                "confidence": "HIGH",
                "evidence": f"Detected technologies: {', '.join(result['technologies'])}",
                "exploits_available": []
            })

        # =========================
        # 🧾 SERVER HEADER DISCLOSURE
        # =========================
        server = response.headers.get("Server")
        if server:
            findings.append({
                "type": "Server Information Disclosure",
                "category": "Information Disclosure",
                "severity": "LOW",
                "url": target,
                "confidence": "MEDIUM",
                "evidence": f"Server header exposed: {server}",
                "exploits_available": []
            })

        # =========================
        # 🧹 CLEAN DATA
        # =========================
        result["links"] = list(set(result["links"]))[:20]
        result["technologies"] = list(set(result["technologies"]))
        result["keywords"] = list(set(result["keywords"]))[:20]

        # =========================
        # 📊 FINAL OUTPUT (PIPELINE READY)
        # =========================
        return {
            "target": target,

            "vulnerabilities": findings,
            "findings": findings,

            "total_urls": len(result["links"]),
            "total_urls_scanned": len(result["links"]),

            "risk": {
                "score": len(findings) * 3,
                "level": "LOW" if len(findings) < 3 else "MEDIUM"
            },

            # extra recon data (nice for reports)
            "recon": result
        }

    except Exception as e:
        return {
            "target": target,
            "vulnerabilities": [],
            "findings": [],
            "total_urls": 0,
            "total_urls_scanned": 0,
            "risk": {
                "score": 0,
                "level": "LOW"
            },
            "error": str(e)
        }