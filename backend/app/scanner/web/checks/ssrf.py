import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import uuid
import copy


def generate_payload(callback_base):
    unique_id = str(uuid.uuid4())
    return f"{unique_id}.{callback_base}", unique_id


def inject_payload(url, param, payload):
    parsed = urlparse(url)
    params = parse_qs(parsed.query)

    params[param] = [payload]

    new_query = urlencode(params, doseq=True)

    return urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment
    ))


def check_ssrf(urls, callback_base, interaction_checker):
    findings = []

    headers = {
        "User-Agent": "Mozilla/5.0 (AI-Scanner/1.0)"
    }

    for url in urls:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)

        if not params:
            continue

        for param in params.keys():
            payload, token = generate_payload(callback_base)

            test_url = inject_payload(url, param, payload)

            try:
                requests.get(test_url, headers=headers, timeout=5)
            except:
                pass

            # 🔥 Check if interaction happened
            if interaction_checker(token):
                findings.append({
                    "type": "Blind SSRF",
                    "category": "A10: SSRF",
                    "severity": "CRITICAL",
                    "url": url,
                    "parameter": param,
                    "payload": payload,
                    "confidence": "HIGH",
                    "evidence": f"Out-of-band interaction detected for token {token}"
                })

    return findings
