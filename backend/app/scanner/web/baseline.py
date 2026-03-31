import hashlib
import json
from datetime import datetime


def generate_baseline(scan_data):
    """
    Create baseline profile of the web application
    """

    pages = scan_data.get("pages", [])
    parameters = scan_data.get("parameters", [])
    technologies = scan_data.get("technologies", [])

    baseline = {
        "timestamp": datetime.utcnow().isoformat(),

        "page_count": len(pages),
        "parameter_count": len(parameters),

        "unique_pages": list(set(pages)),
        "parameters": list(set(parameters)),

        "technologies": technologies,

        "fingerprint": generate_fingerprint(pages, parameters)
    }

    return baseline


def generate_fingerprint(pages, parameters):
    """
    Create a fingerprint for website structure
    """

    data = json.dumps({
        "pages": sorted(pages),
        "parameters": sorted(parameters)
    })

    return hashlib.sha256(data.encode()).hexdigest()


def compare_baseline(old_baseline, new_scan):
    """
    Detect differences between old baseline and new scan
    """

    new_baseline = generate_baseline(new_scan)

    changes = {
        "new_pages": [],
        "new_parameters": [],
        "structure_changed": False
    }

    old_pages = set(old_baseline.get("unique_pages", []))
    new_pages = set(new_baseline.get("unique_pages", []))

    old_params = set(old_baseline.get("parameters", []))
    new_params = set(new_baseline.get("parameters", []))

    changes["new_pages"] = list(new_pages - old_pages)
    changes["new_parameters"] = list(new_params - old_params)

    if old_baseline.get("fingerprint") != new_baseline.get("fingerprint"):
        changes["structure_changed"] = True

    return changes