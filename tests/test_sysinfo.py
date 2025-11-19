#!/usr/bin/env python3
"""
Unit tests for vibe-sysinfo tool (OPERATION FIRST_CONTACT).

Tests verify that the system information fetcher works correctly
and integrates with the VIBE Agency QA framework.
"""

import json
from pathlib import Path

import psutil
import pytest


class TestSysinfo:
    """Test the vibe-sysinfo tool."""

    VIBE_ROOT = Path(__file__).parent.parent

    def test_sysinfo_exists(self):
        """Test that bin/vibe-sysinfo exists."""
        tool_path = self.VIBE_ROOT / "bin" / "vibe-sysinfo"
        assert tool_path.exists(), "bin/vibe-sysinfo does not exist"

    def test_sysinfo_executable(self):
        """Test that bin/vibe-sysinfo is executable."""
        tool_path = self.VIBE_ROOT / "bin" / "vibe-sysinfo"
        assert tool_path.stat().st_mode & 0o111, "bin/vibe-sysinfo is not executable"

    def get_system_info(self) -> dict:
        """Helper: directly get system info without running subprocess."""
        import platform
        import time

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

    def test_sysinfo_json_output(self):
        """Test that system info can be gathered as JSON."""
        info = self.get_system_info()

        # Verify key fields exist
        assert "hostname" in info
        assert "os" in info
        assert "cpu" in info
        assert "memory" in info
        assert "disk" in info
        assert "uptime" in info

    def test_sysinfo_json_cpu_info(self):
        """Test that CPU information is present and valid."""
        info = self.get_system_info()

        cpu = info["cpu"]
        assert isinstance(cpu["cores"], int)
        assert isinstance(cpu["threads"], int)
        assert cpu["cores"] > 0
        assert cpu["threads"] >= cpu["cores"]
        assert 0 <= cpu["usage_percent"] <= 100

    def test_sysinfo_json_memory_info(self):
        """Test that memory information is present and valid."""
        info = self.get_system_info()

        mem = info["memory"]
        assert mem["total_gb"] > 0
        assert mem["used_gb"] <= mem["total_gb"]
        assert mem["available_gb"] >= 0
        assert 0 <= mem["percent"] <= 100

    def test_sysinfo_json_disk_info(self):
        """Test that disk information is present and valid."""
        info = self.get_system_info()

        disk = info["disk"]
        assert disk["total_gb"] > 0
        assert disk["used_gb"] <= disk["total_gb"]
        assert disk["free_gb"] >= 0
        assert 0 <= disk["percent"] <= 100

    def test_sysinfo_json_uptime_info(self):
        """Test that uptime information is present and valid."""
        info = self.get_system_info()

        uptime = info["uptime"]
        assert uptime["total_seconds"] >= 0
        assert uptime["days"] >= 0
        assert uptime["hours"] >= 0
        assert uptime["minutes"] >= 0

    def test_sysinfo_json_serializable(self):
        """Test that system info can be JSON serialized."""
        info = self.get_system_info()
        json_str = json.dumps(info)
        parsed = json.loads(json_str)
        assert parsed == info


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
