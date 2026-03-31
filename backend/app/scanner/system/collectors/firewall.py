import subprocess


def check_firewall(ssh=None):
    """
    Check firewall status.
    """

    try:

        if ssh:
            output = ssh.execute("sudo iptables -L")
        else:
            output = subprocess.getoutput("sudo iptables -L")

        enabled = "Chain" in output

        return {
            "enabled": enabled,
            "rules": output
        }

    except Exception:
        return {
            "enabled": False,
            "rules": ""
        }