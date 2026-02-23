"""
URL Validator
-------------
Validates and inspects URL reachability before running
other web scanners.

Checks performed:
 - URL formatting
 - HTTP/HTTPS scheme
 - DNS resolution
 - HTTP response status
 - Redirects
 - Response time
"""

import re
import json
import socket
import logging
from time import time
from datetime import datetime

import requests


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - URL_VALIDATOR - %(levelname)s - %(message)s"
)
logger = logging.getLogger("url_validator")


def _timestamp() -> str:
    """Return current timestamp ISO format."""
    return datetime.now().isoformat()


# -----------------------------
# 1. URL Format Validation
# -----------------------------
def is_valid_format(url: str) -> bool:
    """
    Validate URL using regex.
    Accepts only http/https.
    """
    pattern = re.compile(
        r"^(https?://)"              # http:// or https://
        r"([A-Za-z0-9.-]+)"          # domain
        r"(\.[A-Za-z]{2,10})"        # .com .net .org etc
        r"(:\d+)?(/.*)?$"            # optional port + path
    )
    return bool(pattern.match(url))


# -----------------------------
# 2. DNS Check
# -----------------------------
def resolve_domain(url: str) -> str:
    """
    Extract hostname from URL and resolve it to an IP.
    Returns IP or raises an exception.
    """
    try:
        hostname = url.split("//")[1].split("/")[0].split(":")[0]
        ip = socket.gethostbyname(hostname)
        return ip
    except Exception as e:
        raise Exception(f"DNS resolution failed: {e}")


# -----------------------------
# 3. HTTP Reachability
# -----------------------------
def check_http(url: str) -> dict:
    """
    Perform HTTP GET request.
    Returns:
     - status code
     - redirect info
     - response time
    """
    try:
        start = time()
        response = requests.get(url, timeout=5, allow_redirects=True)
        elapsed = round((time() - start) * 1000, 2)  # ms

        return {
            "status_code": response.status_code,
            "final_url": response.url,
            "redirected": (response.url != url),
            "response_time_ms": elapsed
        }
    except requests.exceptions.RequestException as e:
        return {
            "error": f"HTTP request failed: {e}"
        }


# -----------------------------
# 4. Main Validator
# -----------------------------
def validate_url(url: str) -> dict:
    """
    Validate URL format, DNS, and HTTP.
    Returns full JSON validation result.
    """
    logger.info("Validating URL: %s", url)

    result = {
        "timestamp": _timestamp(),
        "url": url,
        "valid_format": False,
        "dns_resolved_ip": None,
        "http_result": None
    }

    # Step 1: Format validation
    if not is_valid_format(url):
        result["error"] = "Invalid URL format"
        return result
    result["valid_format"] = True

    # Step 2: DNS resolution
    try:
        ip = resolve_domain(url)
        result["dns_resolved_ip"] = ip
    except Exception as e:
        result["error"] = str(e)
        return result

    # Step 3: HTTP Check
    http_info = check_http(url)
    result["http_result"] = http_info

    logger.info("URL validation completed for %s", url)
    return result


# -----------------------------
# 5. Run as script for testing
# -----------------------------
if __name__ == "__main__":
    test_url = "https://example.com"
    print(json.dumps(validate_url(test_url), indent=4))
