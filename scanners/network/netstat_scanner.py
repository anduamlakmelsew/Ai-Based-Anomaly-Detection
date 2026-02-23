"""
Netstat Scanner Module
----------------------
This module lists all network connections similar to the 'netstat' command.

Author: Student 2 (Backend)
Date: 2025
"""

import psutil
import json
from datetime import datetime


def get_timestamp():
    """Return current timestamp in ISO format."""
    return datetime.now().isoformat()


def scan_netstat():
    """
    Scan all active network connections.

    Returns:
        dict: JSON-friendly list of network connections.
    """
    results = []

    try:
        for conn in psutil.net_connections(kind='inet'):
            try:
                connection_info = {
                    "fd": conn.fd,
                    "family": str(conn.family),
                    "type": str(conn.type),
                    "local_address": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A",
                    "remote_address": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A",
                    "status": conn.status,
                    "pid": conn.pid,
                }

                # try to get process name
                if conn.pid:
                    try:
                        process = psutil.Process(conn.pid)
                        connection_info["process_name"] = process.name()
                    except Exception:
                        connection_info["process_name"] = "Unknown / Access Denied"
                else:
                    connection_info["process_name"] = "N/A"

                results.append(connection_info)

            except Exception:
                results.append({"error": "Failed to read connection"})

        return {
            "timestamp": get_timestamp(),
            "total_connections": len(results),
            "connections": results
        }

    except Exception as e:
        return {
            "timestamp": get_timestamp(),
            "error": str(e)
        }


def scan_netstat_json():
    """
    Return netstat scan result as JSON string.
    """
    return json.dumps(scan_netstat(), indent=4)


# Optional: Run directly
if __name__ == "__main__":
    print(scan_netstat_json())
