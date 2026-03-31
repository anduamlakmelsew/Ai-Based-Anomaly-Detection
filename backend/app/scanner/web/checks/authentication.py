import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin

COMMON_USERNAMES = ["admin", "user", "test"]
COMMON_PASSWORDS = ["admin", "password", "123456", "test"]

LOGIN_KEYWORDS = ["login", "signin", "auth"]


def is_login_page(url):
    return any(k in url.lower() for k in LOGIN_KEYWORDS)


def extract_login_form(html):
    soup = BeautifulSoup(html, "html.parser")

    form = soup.find("form")
    if not form:
        return None

    inputs = form.find_all("input")

    form_data = {}
    username_field = None
    password_field = None

    for inp in inputs:
        name = inp.get("name")
        if not name:
            continue

        if "user" in name.lower() or "email" in name.lower():
            username_field = name
        elif "pass" in name.lower():
            password_field = name

        form_data[name] = ""

    if username_field and password_field:
        return form.get("action"), form_data, username_field, password_field

    return None


def is_login_success(response):
    body = response.text.lower()

    # stronger heuristics
    if response.status_code in [301, 302] and "login" not in response.headers.get("Location", "").lower():
        return True

    if "logout" in body or "dashboard" in body or "welcome" in body:
        return True

    return False


def check_authentication(urls):
    findings = []
    seen = set()

    headers = {
        "User-Agent": "Mozilla/5.0 (AI-Scanner/1.0)"
    }

    for url in urls:
        if not is_login_page(url):
            continue

        try:
            res = requests.get(url, headers=headers, timeout=5)
        except:
            continue

        form_info = extract_login_form(res.text)
        if not form_info:
            continue

        action, form_data, user_field, pass_field = form_info

        login_url = urljoin(url, action) if action else url

        for username in COMMON_USERNAMES:
            for password in COMMON_PASSWORDS:

                form_data[user_field] = username
                form_data[pass_field] = password

                try:
                    login_res = requests.post(
                        login_url,
                        data=form_data,
                        headers=headers,
                        timeout=5,
                        allow_redirects=False
                    )
                except:
                    continue

                if is_login_success(login_res):
                    key = f"{login_url}:{username}:{password}"

                    if key in seen:
                        continue
                    seen.add(key)

                    findings.append({
                        "type": "Weak Authentication",
                        "category": "A07: Identification and Authentication Failures",
                        "severity": "CRITICAL",
                        "url": login_url,
                        "confidence": "HIGH",
                        "evidence": f"Successful login with credentials {username}:{password}",
                        "exploits_available": [],
                        "details": {
                            "username": username,
                            "password": password
                        }
                    })

                time.sleep(1)

    return findings