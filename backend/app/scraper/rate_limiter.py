import asyncio
from datetime import datetime
from collections import defaultdict


class RateLimiter:
    """Ensures minimum delay between requests to same domain"""

    def __init__(self, min_delay_seconds: int = 15):
        self.min_delay = min_delay_seconds
        self.last_request_time = defaultdict(lambda: None)
        self._locks = defaultdict(asyncio.Lock)

    async def wait_if_needed(self, domain: str):
        """Wait if last request to domain was too recent"""
        async with self._locks[domain]:
            last_time = self.last_request_time[domain]
            if last_time:
                elapsed = (datetime.now() - last_time).total_seconds()
                if elapsed < self.min_delay:
                    wait_time = self.min_delay - elapsed
                    await asyncio.sleep(wait_time)

            self.last_request_time[domain] = datetime.now()
