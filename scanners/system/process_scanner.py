
"""
Process Scanner Module
----------------------
This module scans all active running processes and returns
detailed structured JSON data.
"""

import psutil
import json
from datetime import datetime


def get_timestamp():
    """Return current timestamp in ISO format."""
    return datetime.now().isoformat()


def format_time(epoch_time):
    """Convert epoch time to readable datetime. Some processes do not expose start time."""
    try:
        return datetime.fromtimestamp(epoch_time).isoformat()
    except Exception:
        return "N/A"


def scan_processes():
    """
    Scan all currently running processes.

    Returns:
        dict: JSON-friendly process information.
    """
    process_list = []

    try:
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent',
                                         'memory_percent', 'status', 'create_time',
                                         'num_threads']):

            try:
                process_info = {
                    "pid": proc.info.get("pid"),
                    "name": proc.info.get("name"),
                    "user": proc.info.get("username"),
                    "cpu_percent": proc.info.get("cpu_percent"),
                    "memory_percent": round(proc.info.get("memory_percent", 0), 2),
                    "status": proc.info.get("status"),
                    "threads": proc.info.get("num_threads"),
                    "started_at": format_time(proc.info.get("create_time"))
                }

                process_list.append(process_info)

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Process terminated or access blocked
                process_list.append({
                    "pid": proc.pid,
                    "name": "Unknown / Access Denied",
                    "error": "AccessDenied or ProcessEnded"
                })

        result = {
            "timestamp": get_timestamp(),
            "total_processes": len(process_list),
            "processes": process_list
        }

        return result

    except Exception as e:
        return {
            "timestamp": get_timestamp(),
            "error": str(e)
        }


def scan_processes_json():
    """
    Return process scan results as a JSON string.

    Returns:
        str: JSON-formatted scan output.
    """
    return json.dumps(scan_processes(), indent=4)


# Optional: Run directly
if __name__ == "__main__":
    print(scan_processes_json())
