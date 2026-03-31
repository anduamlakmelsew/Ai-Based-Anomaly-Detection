import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import copy
import re


def extract_params(url):
    parsed = urlparse(url)
    return parse_qs(parsed.query)


def rebuild_url(parsed, params):
    query = urlencode(params, doseq=True)
    return urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        query,
        parsed.fragment
    ))


def mutate_value(value):
    mutations = []

    if value.isdigit():
        mutations.append(str(int(value) + 1))
        mutations.append(str(int(value) + 10))

    elif "@" in value:
        mutations.append("test@example.com")
        mutations.append("admin@example.com")

    elif re.match(r"[a-f0-9\-]{8,}", value.lower()):
        mutations.append("00000000-0000-0000-0000-000000000000")

    else:
        mutations.append("test")
        mutations.append("admin")

    return mutations


def response_similarity(r1, r2):
    if not r1 or not r2:
        return 0

    len1 = len(r1.text)
    len2 = len(r2.text)

    if len1 == 0 or len2 == 0:
        return 0

    len_diff = abs(len1 - len2)
    similarity = 1 - (len_diff / max(len1, len2))

    return similarity


def check_idor(urls):
    findings = []

    headers = {
        "User-Agent": "Mozilla/5.0 (AI-Scanner/1.0)"
    }

    for url in urls:
        parsed = urlparse(url)
        params = extract_params(url)

        if not params:
            continue

        try:
            original_res = requests.get(url, headers=headers, timeout=5)
        except:
            continue

        for key, values in params.items():
            for value in values:

                mutations = mutate_value(value)

                for m in mutations:
                    mutated_params = copy.deepcopy(params)
                    mutated_params[key] = [m]

                    mutated_url = rebuild_url(parsed, mutated_params)

                    try:
                        mutated_res = requests.get(mutated_url, headers=headers, timeout=5)
                    except:
                        continue

                    similarity = response_similarity(original_res, mutated_res)

                    # 🔥 STRONGER DETECTION
                    if (
                        mutated_res.status_code == 200
                        and original_res.status_code == 200
                        and similarity > 0.85
                        and mutated_url != url
                    ):
                        findings.append({
                            "type": "IDOR (Insecure Direct Object Reference)",
                            "category": "A01: Broken Access Control",
                            "severity": "HIGH",
                            "url": mutated_url,
                            "confidence": "HIGH",
                            "evidence": f"Parameter '{key}' changed from '{value}' to '{m}' produced similar response ({round(similarity,2)})",
                            "exploits_available": [],
                            "details": {
                                "parameter": key,
                                "original_value": value,
                                "mutated_value": m
                            }
                        })

    return findings