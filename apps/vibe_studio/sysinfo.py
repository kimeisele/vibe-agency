"""System information gathering utilities.

Part of OPERATION FIRST_CONTACT - First real deliverable of VIBE Agency.
"""

import platform
import time

import psutil


def get_system_info() -> dict:
    """Gather comprehensive system information."""
    # OS Information
    os_info = platform.platform()
    hostname = platform.node()

    # CPU Information
    cpu_count = psutil.cpu_count(logical=False)
    cpu_threads = psutil.cpu_count(logical=True)
    cpu_freq = psutil.cpu_freq()
    cpu_percent = psutil.cpu_percent(interval=0.1)

    # Memory Information
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()

    # Disk Information
    disk = psutil.disk_usage("/")

    # Uptime
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time
    uptime_days = int(uptime_seconds // 86400)
    uptime_hours = int((uptime_seconds % 86400) // 3600)
    uptime_minutes = int((uptime_seconds % 3600) // 60)

    return {
        "hostname": hostname,
        "os": os_info,
        "cpu": {
            "cores": cpu_count,
            "threads": cpu_threads,
            "frequency_mhz": cpu_freq.current if cpu_freq else "N/A",
            "usage_percent": cpu_percent,
        },
        "memory": {
            "total_gb": round(memory.total / (1024**3), 2),
            "used_gb": round(memory.used / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2),
            "percent": memory.percent,
        },
        "swap": {
            "total_gb": round(swap.total / (1024**3), 2),
            "used_gb": round(swap.used / (1024**3), 2),
            "free_gb": round(swap.free / (1024**3), 2),
            "percent": swap.percent,
        },
        "disk": {
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "percent": disk.percent,
        },
        "uptime": {
            "days": uptime_days,
            "hours": uptime_hours,
            "minutes": uptime_minutes,
            "total_seconds": int(uptime_seconds),
        },
    }
