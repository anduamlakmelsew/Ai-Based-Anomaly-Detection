import subprocess


def get_installed_packages(ssh=None):
    """
    Collect installed packages.
    """

    try:

        if ssh:
            output = ssh.execute("dpkg -l")
        else:
            output = subprocess.getoutput("dpkg -l")

        packages = []

        for line in output.splitlines():
            if line.startswith("ii"):
                parts = line.split()
                packages.append(parts[1])

        return packages

    except Exception:
        return []