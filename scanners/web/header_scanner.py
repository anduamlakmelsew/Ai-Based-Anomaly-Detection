"""
HTTP Header Scanner
"""

import json
import logging
from time import time
from datetime import datetime

import requests


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - HEADER_SCANNER - %(levelname)s - %(message)s"
)
logger = logging.getLogger("header_scanner")


def _timestamp() -> str:
    """Return timestamp in ISO format."""
    return datetime.now().isoformat()


# -----------------------------------------
# Security headers to check
# -----------------------------------------
REQUIRED_SECURITY_HEADERS = [
    "Strict-Transport-Security",     # HSTS
    "Content-Security-Policy",       # XSS protection
    "X-Frame-Options",               # Clickjacking protection
    "X-Content-Type-Options",        # MIME sniffing
    "Referrer-Policy",
    "Permissions-Policy"
]


# -----------------------------------------
# Try HEAD request first, GET if blocked
# -----------------------------------------
def _fetch_headers(url: str) -> tuple:
    """
    Returns: (headers_dict, response_time_ms)
    """

    start = time()
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        elapsed = round((time() - start) * 1000, 2)
        return response.headers, elapsed

    except Exception:
        logger.warning("HEAD request blocked, trying GET...")

        start = time()
        try:
            response = requests.get(url, timeout=5, allow_redirects=True)
            elapsed = round((time() - start) * 1000, 2)
            return response.headers, elapsed
        except Exception as e:
            raise Exception(f"HTTP request failed: {e}")


# -----------------------------------------
# Analyze header data
# -----------------------------------------
def analyze_headers(headers: dict) -> dict:
    """Analyze security posture & server exposure."""

    # 1. security headers
    missing = [
        header for header in REQUIRED_SECURITY_HEADERS
        if header not in headers
    ]

    # 2. server info
    server = headers.get("Server", "Unknown")
    powered_by = headers.get("X-Powered-By", "Unknown")

    return {
        "server": server,
        "powered_by": powered_by,
        "missing_security_headers": missing
    }


# -----------------------------------------
# Main Scanner
# -----------------------------------------
def scan_headers(url: str) -> dict:
    """
    Main function that scans headers
    and returns structured JSON-friendly result.
    """

    logger.info("Scanning HTTP headers for: %s", url)

    result = {
        "timestamp": _timestamp(),
        "url": url,
        "headers": {},
        "analysis": {},
        "response_time_ms": None,
    }

    try:
        # Step 1: fetch headers
        headers, elapsed = _fetch_headers(url)
        result["headers"] = dict(headers)
        result["response_time_ms"] = elapsed

        # Step 2: analyze headers
        result["analysis"] = analyze_headers(headers)

    except Exception as e:
        result["error"] = str(e)
        logger.error("Header scan error: %s", e)

    return result


# -----------------------------------------
# Script mode for testing
# -----------------------------------------
if __name__ == "__main__":
    test_url = "https://example.com"
    print(json.dumps(scan_headers(test_url), indent=4))
