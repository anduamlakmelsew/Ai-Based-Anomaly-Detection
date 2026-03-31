import subprocess
import re


def discover_hosts(target):
    """
    Discover live hosts in the target network using Nmap ping scan.
    """

    try:
        command = ["nmap", "-sn", target]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )

        output = result.stdout

        hosts = []

        current_host = {}

        for line in output.split("\n"):

            # Detect host
            if "Nmap scan report for" in line:

                ip_match = re.search(r"\((.*?)\)", line)

                if ip_match:
                    ip = ip_match.group(1)
                else:
                    ip = line.split("for")[1].strip()

                current_host = {
                    "ip": ip,
                    "hostname": None,
                    "mac": None,
                    "vendor": None,
                    "open_ports": []
                }

                hosts.append(current_host)

            # Detect MAC address
            if "MAC Address" in line:

                parts = line.split()

                mac = parts[2]

                vendor = " ".join(parts[3:]).replace("(", "").replace(")", "")

                if hosts:
                    hosts[-1]["mac"] = mac
                    hosts[-1]["vendor"] = vendor

        return {
            "success": True,
            "hosts": hosts
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }