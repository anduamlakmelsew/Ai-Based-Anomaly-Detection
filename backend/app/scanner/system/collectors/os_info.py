import platform
import subprocess


def get_os_info(ssh=None):
    """
    Collect OS information.
    Works for both local and remote scans.
    """

    # Remote host
    if ssh:
        system = ssh.execute("uname -s")
        release = ssh.execute("uname -r")
        version = ssh.execute("uname -v")
        architecture = ssh.execute("uname -m")

        return {
            "system": system.strip(),
            "release": release.strip(),
            "version": version.strip(),
            "architecture": architecture.strip()
        }

    # Local host
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "architecture": platform.machine()
    }