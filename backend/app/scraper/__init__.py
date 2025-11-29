"""Scraper package - infrastructure for scraping cycling data."""
from .rate_limiter import RateLimiter
from .scheduler import ScraperScheduler
from .parsers import PCScraper

__all__ = [
    "RateLimiter",
    "ScraperScheduler",
    "PCScraper",
    "create_scheduler",
]


def create_scheduler() -> ScraperScheduler:
    """
    Factory function to create a ScraperScheduler with all available scrapers.
    
    Returns:
        Configured ScraperScheduler instance
    """
    rate_limiter = RateLimiter()
    scrapers = [
        PCScraper(rate_limiter=rate_limiter),
    ]
    return ScraperScheduler(scrapers=scrapers)
