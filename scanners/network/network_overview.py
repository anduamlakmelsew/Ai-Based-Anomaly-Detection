"""
Network Overview Scanner
------------------------
Provides a high-level summary of network interfaces, IP addresses,
default gateway, open connections, and bandwidth usage.

Author: Student 2 (Backend)
Date: 2025
"""

import psutil
import socket
import json
import netifaces
from datetime import datetime


def get_timestamp():
    """Return current timestamp in ISO 8601 format."""
    return datetime.now().isoformat()


def get_hostname():
    """Return system hostname."""
    try:
        return socket.gethostname()
    except:
        return "Unknown"


def get_local_ip():
    """Return primary local IP address."""
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "0.0.0.0"


def get_default_gateway():
    """Return default gateway address."""
    try:
        gateways = netifaces.gateways()
        default = gateways.get('default')
        if default and netifaces.AF_INET in default:
            return default[netifaces.AF_INET][0]
    except:
        pass
    return "Unknown"


def get_interfaces():
    """Return all network interfaces and their IPv4/IPv6 addresses."""
    interfaces = {}

    for iface in netifaces.interfaces():
        try:
            addrs = netifaces.ifaddresses(iface)
            interfaces[iface] = {
                "ipv4": [addr["addr"] for addr in addrs.get(netifaces.AF_INET, [])],
                "ipv6": [addr["addr"] for addr in addrs.get(netifaces.AF_INET6, [])],
                "mac": [addr["addr"] for addr in addrs.get(netifaces.AF_LINK, [])]
            }
        except:
            interfaces[iface] = "Error reading interface"

    return interfaces


def get_bandwidth_usage():
    """Return total bytes sent/received."""
    counters = psutil.net_io_counters()

    return {
        "bytes_sent": counters.bytes_sent,
        "bytes_received": counters.bytes_recv,
        "packets_sent": counters.packets_sent,
        "packets_received": counters.packets_recv
    }


def get_active_connections():
    """Return list of active TCP/UDP connections."""
    connections = []

    for conn in psutil.net_connections():
        try:
            connections.append({
                "type": str(conn.type),
                "family": str(conn.family),
                "laddr": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                "raddr": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                "status": conn.status
            })
        except:
            connections.append({"error": "Access Denied"})

    return connections


def network_overview():
    """Combine all network data into one JSON-ready object."""
    try:
        return {
            "timestamp": get_timestamp(),
            "hostname": get_hostname(),
            "local_ip": get_local_ip(),
            "default_gateway": get_default_gateway(),
            "interfaces": get_interfaces(),
            "bandwidth_usage": get_bandwidth_usage(),
            "active_connections": get_active_connections()
        }
    except Exception as e:
        return {
            "timestamp": get_timestamp(),
            "error": str(e)
        }


def network_overview_json():
    """Return full overview as JSON string."""
    return json.dumps(network_overview(), indent=4)


if __name__ == "__main__":
    print(network_overview_json())
