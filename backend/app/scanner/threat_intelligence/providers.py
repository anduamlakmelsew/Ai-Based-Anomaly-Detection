import requests


ABUSEIPDB_API_KEY = "YOUR_ABUSEIPDB_KEY"
VIRUSTOTAL_API_KEY = "YOUR_VIRUSTOTAL_KEY"


def check_abuseipdb(ip):

    url = "https://api.abuseipdb.com/api/v2/check"

    headers = {
        "Key": ABUSEIPDB_API_KEY,
        "Accept": "application/json"
    }

    params = {
        "ipAddress": ip,
        "maxAgeInDays": 90
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)

        if response.status_code != 200:
            return {"source": "abuseipdb", "error": "API error"}

        data = response.json()["data"]

        return {
            "source": "abuseipdb",
            "ip": ip,
            "abuse_score": data["abuseConfidenceScore"],
            "country": data["countryCode"],
            "usage_type": data["usageType"],
            "isp": data["isp"]
        }

    except Exception as e:
        return {"source": "abuseipdb", "error": str(e)}


def check_virustotal(ip):

    url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"

    headers = {
        "x-apikey": VIRUSTOTAL_API_KEY
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            return {"source": "virustotal", "error": "API error"}

        stats = response.json()["data"]["attributes"]["last_analysis_stats"]

        malicious = stats.get("malicious", 0)

        return {
            "source": "virustotal",
            "ip": ip,
            "malicious_reports": malicious
        }

    except Exception as e:
        return {"source": "virustotal", "error": str(e)}