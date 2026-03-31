import requests
from bs4 import BeautifulSoup


TECH_SIGNATURES = {
    "wordpress": ["wp-content", "wp-includes"],
    "drupal": ["drupal-settings-json"],
    "joomla": ["joomla"],
    "django": ["csrftoken"],
    "laravel": ["laravel_session"],
    "react": ["react"],
    "angular": ["ng-version"],
}


HEADER_SIGNATURES = {
    "nginx": "nginx",
    "apache": "apache",
    "iis": "microsoft-iis"
}


def detect_from_headers(headers):

    detected = []

    server = headers.get("Server", "").lower()

    for tech, signature in HEADER_SIGNATURES.items():

        if signature in server:
            detected.append(tech)

    return detected


def detect_from_html(html):

    detected = []

    html_lower = html.lower()

    for tech, signatures in TECH_SIGNATURES.items():

        for sig in signatures:

            if sig in html_lower:
                detected.append(tech)

    return detected


def detect_technology(url):

    try:

        response = requests.get(url, timeout=5)

        headers = response.headers
        html = response.text

        detected = []

        detected += detect_from_headers(headers)
        detected += detect_from_html(html)

        soup = BeautifulSoup(html, "lxml")

        generator = soup.find("meta", attrs={"name": "generator"})

        if generator:
            detected.append(generator.get("content"))

        detected = list(set(detected))

        return {
            "success": True,
            "technologies": detected
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }