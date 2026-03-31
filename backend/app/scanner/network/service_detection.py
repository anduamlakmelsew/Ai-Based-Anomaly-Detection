import subprocess
import re

def detect_services(target):
    try:
        command = [
            "nmap",
            "-sV",
            "-Pn",
            target
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )

        output = result.stdout
        services = []

        for line in output.split("\n"):

            if re.match(r"^\d+\/tcp", line):

                parts = line.split()

                port = parts[0].split("/")[0]
                state = parts[1]

                if state != "open":
                    continue

                service = parts[2] if len(parts) > 2 else None
                version = " ".join(parts[3:]) if len(parts) > 3 else None

                services.append({
                    "host": target,
                    "port": int(port),
                    "state": state,
                    "service": service,
                    "version": version
                })

        return {
            "success": True,
            "services": services
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }