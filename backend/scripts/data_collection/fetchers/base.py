"""Base classes and utilities for all fetchers"""
import time
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """Shared rate limiting functionality"""

    def __init__(self, rate_limit_rpm: int):
        self.rate_limit = rate_limit_rpm
        self.last_request_time = 0

    def wait(self):
        """Enforce rate limiting"""
        elapsed = time.time() - self.last_request_time
        min_interval = 60.0 / self.rate_limit
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self.last_request_time = time.time()
