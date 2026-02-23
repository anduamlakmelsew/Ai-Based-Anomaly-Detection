
"""
System Overview Scanner
-----------------------
Aggregates CPU, RAM, Disk and Process scanners into a single
system snapshot. Provides:
 - a combined JSON report
 - a short human-readable summary
 - an optional save-to-disk helper

Assumes the individual scanners exist and provide dict outputs:
 - scanners.system.cpu_scanner.get_cpu_info()
 - scanners.system.ram_scanner.scan_ram()
 - scanners.system.disk_scanner.scan_disk()
 - scanners.system.process_scanner.scan_processes()

"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Import scanner functions (adjust import paths if needed)
from scanners.system.cpu_scanner import get_cpu_info
from scanners.system.ram_scanner import scan_ram
from scanners.system.disk_scanner import scan_disk
from scanners.system.process_scanner import scan_processes

# Logger setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - SYSTEM_OVERVIEW - %(levelname)s - %(message)s"
)
logger = logging.getLogger("system_overview")


def _timestamp_iso() -> str:
    """Return current ISO 8601 timestamp."""
    return datetime.now().isoformat()


def build_summary(cpu: Dict[str, Any], ram: Dict[str, Any], disk: Dict[str, Any], processes: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build a short summary from individual scanner outputs.
    Summary contains:
      - cpu_percent (overall)
      - ram_percent (overall)
      - disk_percent (max partition usage)
      - top_processes_by_cpu (top 5)
    """
    try:
        cpu_pct = cpu.get("cpu_percent") if isinstance(cpu, dict) else None
        ram_pct = None
        if isinstance(ram, dict):
            ram_info = ram.get("ram") or {}
            ram_pct = ram_info.get("percent_used")

        # disk: find max percent_used across partitions (if any)
        disk_percent = None
        if isinstance(disk, dict):
            parts = disk.get("disk_partitions") or []
            if parts:
                maxp = max((p.get("percent_used", 0) for p in parts if isinstance(p, dict)), default=0)
                disk_percent = round(maxp, 2)

        # processes: pick top 5 by cpu_percent if available
        top_procs = []
        if isinstance(processes, dict):
            proc_list = processes.get("processes") or []
            # filter valid items with cpu_percent
            valid = [p for p in proc_list if isinstance(p, dict) and isinstance(p.get("cpu_percent"), (int, float))]
            sorted_procs = sorted(valid, key=lambda x: x.get("cpu_percent", 0), reverse=True)
            for p in sorted_procs[:5]:
                top_procs.append({
                    "pid": p.get("pid"),
                    "name": p.get("name"),
                    "cpu_percent": p.get("cpu_percent"),
                    "memory_percent": p.get("memory_percent")
                })

        return {
            "cpu_percent": cpu_pct,
            "ram_percent": ram_pct,
            "disk_max_percent": disk_percent,
            "top_processes_by_cpu": top_procs
        }

    except Exception as e:
        logger.exception("Error while building summary")
        return {"error": str(e)}


def system_overview() -> Dict[str, Any]:
    """
    Run all scanners and return a combined overview dict:
      {
        "timestamp": "...",
        "cpu": { ... },
        "ram": { ... },
        "disk": { ... },
        "processes": { ... },
        "summary": { ... }
      }
    """
    logger.info("Starting system overview scan")
    timestamp = _timestamp_iso()

    # Run scanners (each returns a dict; robust to errors)
    try:
        cpu = get_cpu_info()
    except Exception as e:
        logger.exception("CPU scanner error")
        cpu = {"error": f"cpu scanner failed: {e}"}

    try:
        ram = scan_ram()
    except Exception as e:
        logger.exception("RAM scanner error")
        ram = {"error": f"ram scanner failed: {e}"}

    try:
        disk = scan_disk()
    except Exception as e:
        logger.exception("Disk scanner error")
        disk = {"error": f"disk scanner failed: {e}"}

    try:
        processes = scan_processes()
    except Exception as e:
        logger.exception("Process scanner error")
        processes = {"error": f"process scanner failed: {e}"}

    # Build summary
    summary = build_summary(cpu, ram, disk, processes)

    # Combined result
    result = {
        "timestamp": timestamp,
        "cpu": cpu,
        "ram": ram,
        "disk": disk,
        "processes": processes,
        "summary": summary
    }

    logger.info("System overview scan completed")
    return result


def save_system_overview(result: Dict[str, Any], filename: Optional[str] = None) -> str:
    """
    Save the system overview dict to JSON file.
    If filename is not provided, uses timestamp-based filename.
    Returns the filename used.
    """
    filename = filename or f"system_overview_{datetime.now().strftime('%Y%m%dT%H%M%S')}.json"
    try:
        with open(filename, "w") as f:
            json.dump(result, f, indent=4)
        logger.info("Saved system overview to %s", filename)
        return filename
    except Exception as e:
        logger.exception("Failed to save system overview")
        raise


# Allow running as script for quick tests
if __name__ == "__main__":
    overview = system_overview()
    print(json.dumps(overview, indent=2))
