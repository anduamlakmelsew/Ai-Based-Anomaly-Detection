"""
Port Scanner Module
------------------
"""

import socket
import json
from datetime import datetime


def get_timestamp():
    """Return current timestamp in ISO format."""
    return datetime.now().isoformat()


def scan_port(host, port, timeout=1):
    """
    Scan a single port.
    
    Args:
        host (str): Target IP or hostname.
        port (int): Port number.
        timeout (int): Connection timeout in seconds.

    Returns:
        dict: Result of scanning this port.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)

        result = sock.connect_ex((host, port))
        sock.close()

        return {
            "port": port,
            "status": "open" if result == 0 else "closed"
        }

    except Exception as e:
        return {
            "port": port,
            "status": "error",
            "message": str(e)
        }


def scan_ports(host, start_port=1, end_port=1024):
    """
    Scan a range of ports on a target host.

    Args:
        host (str): Target IP or hostname.
        start_port (int): Starting port.
        end_port (int): Ending port.

    Returns:
        dict: Summary of port scan.
    """
    results = []

    try:
        for port in range(start_port, end_port + 1):
            result = scan_port(host, port)
            results.append(result)

        return {
            "timestamp": get_timestamp(),
            "target_host": host,
            "ports_scanned": f"{start_port}-{end_port}",
            "open_ports": [r["port"] for r in results if r["status"] == "open"],
            "results": results
        }

    except Exception as e:
        return {
            "timestamp": get_timestamp(),
            "error": str(e)
        }


def scan_ports_json(host, start_port=1, end_port=1024):
    """
    Return port scan results as JSON string.

    Returns:
        str: JSON output.
    """
    return json.dumps(scan_ports(host, start_port, end_port), indent=4)


# Optional standalone run
if __name__ == "__main__":
    target = input("Enter target host (e.g., 192.168.1.1): ")
    print(scan_ports_json(target))
