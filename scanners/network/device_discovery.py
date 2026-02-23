"""
Device Discovery Scanner
------------------------
"""

from datetime import datetime
import json
from scapy.all import ARP, Ether, srp


def get_timestamp():
    """Return current timestamp in ISO standard format."""
    return datetime.now().isoformat()


def discover_devices(target_range="192.168.1.0/24"):
    """
    Scan the network to discover active devices using ARP.

    Args:
        target_range (str): The network range to scan.

    Returns:
        dict: JSON-friendly list of discovered hosts.
    """
    try:
        # Create ARP request packet + Ethernet broadcast frame
        arp_request = ARP(pdst=target_range)
        broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")

        packet = broadcast / arp_request

        # Send packet and collect responses
        answered, _ = srp(packet, timeout=2, verbose=False)

        devices = []

        for send, receive in answered:
            devices.append({
                "ip": receive.psrc,
                "mac_address": receive.hwsrc,
                "vendor": "Unknown"  # Placeholder – vendor lookup can be added later
            })

        return {
            "timestamp": get_timestamp(),
            "target_range": target_range,
            "total_devices": len(devices),
            "devices": devices
        }

    except Exception as e:
        return {
            "timestamp": get_timestamp(),
            "error": str(e)
        }


def discover_devices_json(target_range="192.168.1.0/24"):
    """
    Returns scan results as formatted JSON.

    Returns:
        str: JSON string of device discovery.
    """
    return json.dumps(discover_devices(target_range), indent=4)


# Run directly for testing
if __name__ == "__main__":
    print(discover_devices_json())
