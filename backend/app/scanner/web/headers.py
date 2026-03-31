import requests


REQUIRED_SECURITY_HEADERS = [
    "Content-Security-Policy",
    "Strict-Transport-Security",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Referrer-Policy"
]


DANGEROUS_HEADERS = [
    "Server",
    "X-Powered-By"
]


def analyze_headers(url):

    try:

        response = requests.get(url, timeout=5)

        headers = response.headers

        missing_headers = []
        exposed_headers = []

        for header in REQUIRED_SECURITY_HEADERS:

            if header not in headers:
                missing_headers.append(header)

        for header in DANGEROUS_HEADERS:

            if header in headers:
                exposed_headers.append({
                    "header": header,
                    "value": headers.get(header)
                })

        return {
            "success": True,
            "missing_security_headers": missing_headers,
            "dangerous_headers": exposed_headers
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }