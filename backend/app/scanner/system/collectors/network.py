import psutil

def collect_network_info():
    """
    Collect basic network information:
    - Interfaces
    - IP addresses
    - Connections
    """
    try:
        interfaces = psutil.net_if_addrs()
        connections = psutil.net_connections()

        interface_data = {}

        for interface, addrs in interfaces.items():
            interface_data[interface] = []
            for addr in addrs:
                interface_data[interface].append({
                    "family": str(addr.family),
                    "address": addr.address,
                    "netmask": addr.netmask,
                    "broadcast": addr.broadcast
                })

        connection_data = []
        for conn in connections[:50]:  # limit for performance
            connection_data.append({
                "fd": conn.fd,
                "family": str(conn.family),
                "type": str(conn.type),
                "laddr": str(conn.laddr),
                "raddr": str(conn.raddr),
                "status": conn.status
            })

        return {
            "interfaces": interface_data,
            "connections": connection_data
        }

    except Exception as e:
        return {"error": str(e)}