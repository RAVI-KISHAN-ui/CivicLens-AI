"""Device profiles for desktop and throttled mobile emulation.
Reference: Section 7.2 of AGENTS.md.
"""

from typing import Any

DESKTOP_PROFILE = {
    "name": "desktop-1440",
    "viewport": {"width": 1440, "height": 900},
    "device_scale_factor": 1,
    "is_mobile": False,
    "has_touch": False,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 CivicLensBot/0.1",
    "network_conditions": None,  # unthrottled
    "cpu_throttle_rate": 1,
}

MOBILE_PROFILE = {
    "name": "android-midrange-throttled",
    "viewport": {"width": 360, "height": 800},
    "device_scale_factor": 2,
    "is_mobile": True,
    "has_touch": True,
    "user_agent": "Mozilla/5.0 (Linux; Android 13; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36 CivicLensBot/0.1",
    "network_conditions": {
        "offline": False,
        "latency": 150,  # 150 ms RTT
        "downloadThroughput": 1600 * 1024 // 8,  # ~1.6 Mbps down
        "uploadThroughput": 750 * 1024 // 8,     # ~750 kbps up
    },
    "cpu_throttle_rate": 4,  # 4x CPU throttle
}


def get_profile(device: str) -> dict[str, Any]:
    if device in ("mobile", "android-midrange-throttled"):
        return MOBILE_PROFILE
    return DESKTOP_PROFILE
