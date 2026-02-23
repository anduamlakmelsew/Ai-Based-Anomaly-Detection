import requests
import re

def technology_fingerprint(url):
    try:
        response = requests.get(url, timeout=5)
        headers = response.headers
        html = response.text

        technologies = []

        # Server
        server = headers.get("Server")
        if server:
            technologies.append(f"Server: {server}")

        # X-Powered-By
        powered = headers.get("X-Powered-By")
        if powered:
            technologies.append(f"Backend: {powered}")

        # WordPress
        if "wp-content" in html.lower() or "wp-includes" in html.lower():
            technologies.append("CMS: WordPress")

        # React
        if re.search(r"react|react-dom", html, re.IGNORECASE):
            technologies.append("Frontend: React")

        # jQuery
        if re.search(r"jquery", html, re.IGNORECASE):
            technologies.append("Frontend: jQuery")

        # Bootstrap
        if re.search(r"bootstrap.*css", html, re.IGNORECASE):
            technologies.append("CSS Framework: Bootstrap")

        # Cloudflare
        if "cloudflare" in str(headers).lower():
            technologies.append("CDN: Cloudflare")

        if not technologies:
            return ["No known technologies detected"]

        return technologies

    except Exception as e:
        return [f"Error: {str(e)}"]


if __name__ == "__main__":
    url = input("Enter URL: ")
    results = technology_fingerprint(url)
    for tech in results:
        print(tech)
