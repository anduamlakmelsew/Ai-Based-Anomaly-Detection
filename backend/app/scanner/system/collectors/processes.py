import psutil

def get_running_processes():
    """
    Collect running processes (PID and name)
    """
    processes = []

    try:
        for proc in psutil.process_iter(attrs=["pid", "name"]):
            processes.append(proc.info)

    except Exception as e:
        print(f"Error collecting processes: {e}")

    return processes