import subprocess

def get_services(ssh=None):
    """
    Collect running services on the system.
    If `ssh` is provided, run the command over SSH.
    """
    try:
        if ssh:
            # Assume `ssh` has an `execute` method
            output = ssh.execute("systemctl list-units --type=service --state=running")
        else:
            output = subprocess.getoutput(
                "systemctl list-units --type=service --state=running"
            )

        services = []
        for line in output.splitlines():
            if ".service" in line:
                services.append(line.split()[0])  # get service name only

        return services

    except Exception as e:
        print(f"Error collecting services: {e}")
        return []