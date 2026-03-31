import subprocess
import xml.etree.ElementTree as ET


def enumerate_services(target):
    """
    Perform deep service enumeration using Nmap NSE scripts
    """

    try:

        command = [
            "nmap",
            "-sV",            # service detection
            "-O",             # OS detection
            "--script",
            "vuln",           # vulnerability scripts
            "-oX",
            "-",              # XML output
            target
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )

        xml_output = result.stdout

        root = ET.fromstring(xml_output)

        vulnerabilities = []

        for host in root.findall("host"):

            address = host.find("address").get("addr")

            ports = host.find("ports")

            if ports is None:
                continue

            for port in ports.findall("port"):

                portid = port.get("portid")

                scripts = port.findall("script")

                for script in scripts:

                    vulnerabilities.append({
                        "host": address,
                        "port": portid,
                        "script_id": script.get("id"),
                        "output": script.get("output")
                    })

        return {
            "success": True,
            "vulnerabilities": vulnerabilities
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }