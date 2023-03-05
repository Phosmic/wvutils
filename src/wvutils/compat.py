"""Compatibility Variables and Functions

This module contains variables and functions that are used to provide
compatibility across different Python versions and operating systems.
"""

import logging
import sys
import time

__all__ = [
    "preferred_clock",
]

logger = logging.getLogger(__name__)


# Preferred clock, based on which one is more accurate on a given system
if sys.platform == "win32":
    preferred_clock = time.perf_counter
else:
    preferred_clock = time.time
