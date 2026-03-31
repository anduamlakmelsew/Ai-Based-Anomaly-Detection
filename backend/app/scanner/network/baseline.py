"""
Baseline Engine

Creates baseline profile of network assets
and detects anomalies in future scans.
"""


class NetworkBaseline:

    def __init__(self):
        self.baseline = {
            "hosts": [],
            "ports": {},
            "services": {}
        }

    def create(self, discovery_data, scan_data):
        """
        Build baseline from first scan
        """

        hosts = discovery_data.get("hosts", [])
        open_ports = scan_data.get("open_ports", [])
        services = scan_data.get("services", [])

        self.baseline["hosts"] = hosts
        self.baseline["ports"] = open_ports
        self.baseline["services"] = services

        return self.baseline

    def compare(self, discovery_data, scan_data):
        """
        Compare current scan with baseline
        """

        anomalies = []

        new_hosts = set(discovery_data.get("hosts", [])) - set(self.baseline["hosts"])

        if new_hosts:
            anomalies.append({
                "type": "NEW_HOST",
                "hosts": list(new_hosts)
            })

        new_ports = set(scan_data.get("open_ports", [])) - set(self.baseline["ports"])

        if new_ports:
            anomalies.append({
                "type": "NEW_PORT",
                "ports": list(new_ports)
            })

        new_services = set(scan_data.get("services", [])) - set(self.baseline["services"])

        if new_services:
            anomalies.append({
                "type": "NEW_SERVICE",
                "services": list(new_services)
            })

        return anomalies