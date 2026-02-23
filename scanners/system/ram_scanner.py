"""
RAM Scanner Module
------------------
This module scans system RAM usage and returns structured JSON data.

"""

import psutil
import json
from datetime import datetime


def get_timestamp():
    """Return current timestamp in ISO format."""
    return datetime.now().isoformat()


def scan_ram():
    """
    Scan the current RAM usage.
    
    Returns:
        dict: JSON-friendly data about RAM stats.
    """
    try:
        ram = psutil.virtual_memory()

        data = {
            "timestamp": get_timestamp(),
            "ram": {
                "total_mb": round(ram.total / (1024 ** 2), 2),
                "available_mb": round(ram.available / (1024 ** 2), 2),
                "used_mb": round(ram.used / (1024 ** 2), 2),
                "free_mb": round(ram.free / (1024 ** 2), 2),
                "percent_used": ram.percent,
            }
        }

        return data

    except Exception as e:
        return {
            "timestamp": get_timestamp(),
            "error": str(e)
        }


def scan_ram_json():
    """
    Returns RAM scan result as JSON string.
    
    Returns:
        str: JSON-formatted scan output.
    """
    return json.dumps(scan_ram(), indent=4)


# Optional: Run as standalone script
if __name__ == "__main__":
    print(scan_ram_json())
