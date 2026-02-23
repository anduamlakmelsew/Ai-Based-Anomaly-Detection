"""
Disk Scanner Module
-------------------
This module scans disk usage for all mounted partitions
and returns structured JSON data.
"""

import psutil
import json
from datetime import datetime


def get_timestamp():
    """Return current timestamp in ISO format."""
    return datetime.now().isoformat()


def scan_disk():
    """
    Scan disk usage for all partitions.

    Returns:
        dict: JSON-friendly data about each disk.
    """
    try:
        partitions = psutil.disk_partitions(all=False)
        disk_data = []

        for p in partitions:
            try:
                usage = psutil.disk_usage(p.mountpoint)

                disk_info = {
                    "device": p.device,
                    "mountpoint": p.mountpoint,
                    "fstype": p.fstype,
                    "total_gb": round(usage.total / (1024 ** 3), 2),
                    "used_gb": round(usage.used / (1024 ** 3), 2),
                    "free_gb": round(usage.free / (1024 ** 3), 2),
                    "percent_used": usage.percent
                }

                disk_data.append(disk_info)

            except PermissionError:
                # Some partitions cannot be accessed
                disk_data.append({
                    "device": p.device,
                    "mountpoint": p.mountpoint,
                    "error": "Permission Denied"
                })

        result = {
            "timestamp": get_timestamp(),
            "disk_partitions": disk_data
        }

        return result

    except Exception as e:
        return {
            "timestamp": get_timestamp(),
            "error": str(e)
        }


def scan_disk_json():
    """
    Return disk scan results as a JSON string.

    Returns:
        str: JSON-formatted scan output.
    """
    return json.dumps(scan_disk(), indent=4)


# Optional: Run as standalone script
if __name__ == "__main__":
    print(scan_disk_json())

