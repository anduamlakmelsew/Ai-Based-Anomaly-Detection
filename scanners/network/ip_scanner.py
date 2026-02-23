"""
IP Scanner Module
-----------------
"""

import psutil
import json
import socket
import subprocess
from datetime import datetime


# ---------------------------
# Helper: Timestamp
# ---------------------------
def get_timestamp():
    """Return current timestamp in ISO format."""
    return datetime.now().isoformat()


# ---------------------------
# 1. Get Local IP Address
# ---------------------------
def get_local_ip():
    """Return the primary local IP address."""
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return local_ip
    except:
        return "Unable to detect"


# ---------------------------
# 2. Get Public IP Address
# ---------------------------
def get_public_ip():
    """Return public IP using external service (Linux: curl)."""
    try:
        result = subprocess.check_output(
            ["curl", "-s", "https://api.ipify.org"],
            timeout=3
        )
        return result.decode().strip()
    except:
        return "Unable to detect"


# ---------------------------
# 3. Network Interfaces
# ---------------------------
def get_network_interfaces():
    """Get all network interfaces and their IPs."""
    interfaces = {}

    for name, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET:
                interfaces[name] = {
                    "ip": addr.address,
                    "netmask": addr.netmask,
                    "broadcast": addr.broadcast
                }

    return interfaces


# ---------------------------
# 4. Ping Sweep for Active Hosts
# ---------------------------
def ping_ip(ip):
    """Ping a single IP. Return True if alive."""
    try:
        output = subprocess.call(
            ["ping", "-c", "1", "-W", "200", ip],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return output == 0
    except:
        return False


def detect_active_hosts(base_ip):
    """
    Scan IP range 1-254.
    Example: For 192.168.1.X → scan 192.168.1.1 → 192.168.1.254
    """
    active = []

    print(f"[+] Scanning network: {base_ip}.0/24 ...")

    for i in range(1, 255):
        ip = f"{base_ip}.{i}"

        if ping_ip(ip):
            active.append(ip)

    return active


# ---------------------------
# 5. Main Scanner
# ---------------------------
def scan_ip_network():
    try:
        local_ip = get_local_ip()

        # Extract /24
        try:
            base_ip = ".".join(local_ip.split(".")[:3])
        except:
            base_ip = None

        result = {
            "timestamp": get_timestamp(),
            "local_ip": local_ip,
            "public_ip": get_public_ip(),
            "interfaces": get_network_interfaces(),
            "active_hosts": detect_active_hosts(base_ip) if base_ip else []
        }

        return result

    except Exception as e:
        return {
            "timestamp": get_timestamp(),
            "error": str(e)
        }


def scan_ip_network_json():
    """Return JSON version."""
    return json.dumps(scan_ip_network(), indent=4)


# ---------------------------
# Run standalone
# ---------------------------
if __name__ == "__main__":
    print(scan_ip_network_json())
