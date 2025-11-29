from abc import ABC, abstractmethod
from typing import Optional, Dict
import httpx
from app.scraper.rate_limiter import RateLimiter


class BaseScraper(ABC):
    """Base class for all scrapers"""

    def __init__(self, rate_limiter: RateLimiter):
        self.rate_limiter = rate_limiter
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "CyclingLineageBot/1.0 (Educational; https://github.com/yourrepo)",
            },
        )

    @property
    @abstractmethod
    def domain(self) -> str:
        """Domain this scraper targets"""
        pass

    async def fetch(self, url: str) -> Optional[str]:
        """Fetch URL with rate limiting"""
        await self.rate_limiter.wait_if_needed(self.domain)

        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.text
        except httpx.HTTPError as e:
            print(f"Error fetching {url}: {e}")
            return None

    @abstractmethod
    async def scrape_team(self, team_identifier: str) -> Optional[Dict]:
        """Scrape data for a specific team"""
        pass

    async def close(self):
        """Clean up resources"""
        await self.client.aclose()
