"""
CPU Scanner Module 
-----------------------------------------

"""

import psutil
import logging
import json
from datetime import datetime
from typing import Dict, Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - CPU_SCANNER - %(levelname)s - %(message)s"
)

def get_cpu_info() -> Dict[str, Any]:
    """
    Collects CPU performance data.

    Returns:
        dict: A structured dictionary containing CPU metrics and timestamp.
    """
    try:
        logging.info("Starting CPU scan...")

        cpu_percent = psutil.cpu_percent(interval=1)
        per_core_usage = psutil.cpu_percent(interval=1, percpu=True)
        freq = psutil.cpu_freq()
        cores_logical = psutil.cpu_count()
        cores_physical = psutil.cpu_count(logical=False)

        # Load average (Linux/Unix)
        try:
            load_avg = psutil.getloadavg()
        except Exception:
            load_avg = (0, 0, 0)

        # CPU temperature (if supported)
        temp = None
        try:
            temps = psutil.sensors_temperatures()
            if "coretemp" in temps:
                temp = temps["coretemp"][0].current
        except Exception:
            temp = None

        # Timestamp (ISO 8601 format)
        timestamp = datetime.now().isoformat()

        result = {
            "timestamp": timestamp,
            "cpu_percent": cpu_percent,
            "per_core_usage": per_core_usage,
            "frequency": {
                "current": freq.current if freq else None,
                "min": freq.min if freq else None,
                "max": freq.max if freq else None
            },
            "cores": {
                "logical": cores_logical,
                "physical": cores_physical
            },
            "load_average": {
                "1min": load_avg[0],
                "5min": load_avg[1],
                "15min": load_avg[2]
            },
            "temperature": temp
        }

        logging.info("CPU scan completed successfully.")
        return result

    except Exception as e:
        logging.error(f"CPU scan failed: {e}")
        return {"error": str(e)}


def save_cpu_info_to_json(filename: str = "cpu_report.json") -> None:
    """
    Saves CPU scan results to a JSON file.

    Args:
        filename (str): The output JSON file name.
    """
    try:
        data = get_cpu_info()
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)
        logging.info(f"CPU scan saved to {filename}")

    except Exception as e:
        logging.error(f"Failed to save JSON: {e}")