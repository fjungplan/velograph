import asyncio
from typing import List, Dict
from app.scraper.base import BaseScraper
from app.scraper.rate_limiter import RateLimiter


class ScraperScheduler:
    """Round-robin scheduler for multiple scrapers"""

    def __init__(self, scrapers: List[BaseScraper], rate_limiter: RateLimiter):
        self.scrapers = scrapers
        self.rate_limiter = rate_limiter
        self._running = False

    async def run_once(self, team_identifier: str) -> Dict:
        """Run all scrapers once for a team"""
        results = {}

        for scraper in self.scrapers:
            try:
                result = await scraper.scrape_team(team_identifier)
                if result:
                    results[scraper.__class__.__name__] = result
            except Exception as e:
                print(f"Error in {scraper.__class__.__name__}: {e}")
                # Continue with other scrapers

        return results

    async def run_continuous(self, team_identifiers: List[str], interval_seconds: int = 300):
        """Continuously scrape teams in round-robin fashion"""
        self._running = True

        while self._running:
            for team_id in team_identifiers:
                if not self._running:
                    break

                await self.run_once(team_id)
                await asyncio.sleep(interval_seconds)

    def stop(self):
        """Stop the scheduler"""
        self._running = False

    async def close(self):
        """Clean up all scrapers"""
        for scraper in self.scrapers:
            await scraper.close()
