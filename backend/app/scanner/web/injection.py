import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import copy

SQL_PAYLOADS = [
    "' OR '1'='1",
    "' OR 1=1--",
    "\" OR \"1\"=\"1"
]

XSS_PAYLOADS = [
    "<script>alert(1)</script>",
    "\"><script>alert(1)</script>"
]

CMD_PAYLOADS = [
    "; whoami",
    "&& whoami",
    "| whoami"
]


def inject_payload(url, param, payload):
    parsed = urlparse(url)
    query = parse_qs(parsed.query)

    mutated = copy.deepcopy(query)
    mutated[param] = [payload]

    new_query = urlencode(mutated, doseq=True)

    new_url = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment
    ))

    try:
        r = requests.get(new_url, timeout=5)
        return r, new_url
    except Exception:
        return None, new_url


# -----------------------------
# SQL Injection
# -----------------------------
def test_sql_injection(url):
    parsed = urlparse(url)
    params = parse_qs(parsed.query)

    findings = []

    SQL_ERRORS = [
        "sql syntax",
        "mysql",
        "warning",
        "postgres",
        "sqlite",
        "odbc",
        "unclosed quotation"
    ]

    for param in params:
        for payload in SQL_PAYLOADS:

            res, test_url = inject_payload(url, param, payload)
            if not res:
                continue

            body = res.text.lower()

            if any(err in body for err in SQL_ERRORS):
                findings.append({
                    "type": "SQL Injection",
                    "category": "A03: Injection",
                    "severity": "CRITICAL",
                    "url": test_url,
                    "confidence": "HIGH",
                    "evidence": f"SQL error detected using payload: {payload}",
                    "exploits_available": [],
                    "details": {
                        "parameter": param,
                        "payload": payload
                    }
                })

    return findings


# -----------------------------
# XSS
# -----------------------------
def test_xss(url):
    parsed = urlparse(url)
    params = parse_qs(parsed.query)

    findings = []

    for param in params:
        for payload in XSS_PAYLOADS:

            res, test_url = inject_payload(url, param, payload)
            if not res:
                continue

            if payload in res.text:
                findings.append({
                    "type": "Cross-Site Scripting (XSS)",
                    "category": "A03: Injection",
                    "severity": "HIGH",
                    "url": test_url,
                    "confidence": "HIGH",
                    "evidence": f"Payload reflected in response: {payload}",
                    "exploits_available": [],
                    "details": {
                        "parameter": param,
                        "payload": payload
                    }
                })

    return findings


# -----------------------------
# Command Injection
# -----------------------------
def test_command_injection(url):
    parsed = urlparse(url)
    params = parse_qs(parsed.query)

    findings = []

    INDICATORS = [
        "uid=",
        "gid=",
        "root",
        "www-data"
    ]

    for param in params:
        for payload in CMD_PAYLOADS:

            res, test_url = inject_payload(url, param, payload)
            if not res:
                continue

            body = res.text.lower()

            if any(ind in body for ind in INDICATORS):
                findings.append({
                    "type": "Command Injection",
                    "category": "A03: Injection",
                    "severity": "CRITICAL",
                    "url": test_url,
                    "confidence": "HIGH",
                    "evidence": f"Command execution indicator found using payload: {payload}",
                    "exploits_available": [],
                    "details": {
                        "parameter": param,
                        "payload": payload
                    }
                })

    return findings


# -----------------------------
# MAIN RUNNER
# -----------------------------
def run_injection_tests(url):
    findings = []

    findings += test_sql_injection(url)
    findings += test_xss(url)
    findings += test_command_injection(url)

    # remove duplicates
    unique = []
    seen = set()

    for f in findings:
        key = f["type"] + f["url"]
        if key not in seen:
            seen.add(key)
            unique.append(f)

    return unique