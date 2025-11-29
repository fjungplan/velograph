import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from app.scraper.scheduler import ScraperScheduler
from app.scraper.base import BaseScraper
from app.scraper.rate_limiter import RateLimiter


# Mock scrapers for testing
class MockScraperA(BaseScraper):
    @property
    def domain(self) -> str:
        return "scraper-a.com"

    async def scrape_team(self, team_identifier: str):
        await asyncio.sleep(0.01)  # Simulate work
        return {"source": "A", "team": team_identifier}


class MockScraperB(BaseScraper):
    @property
    def domain(self) -> str:
        return "scraper-b.com"

    async def scrape_team(self, team_identifier: str):
        await asyncio.sleep(0.01)  # Simulate work
        return {"source": "B", "team": team_identifier}


class FailingScraper(BaseScraper):
    @property
    def domain(self) -> str:
        return "failing.com"

    async def scrape_team(self, team_identifier: str):
        raise Exception("Scraper failed")


@pytest.fixture
def rate_limiter():
    return RateLimiter(min_delay_seconds=0)


@pytest.fixture
def scrapers(rate_limiter):
    return [MockScraperA(rate_limiter), MockScraperB(rate_limiter)]


@pytest.fixture
def scheduler(scrapers, rate_limiter):
    return ScraperScheduler(scrapers, rate_limiter)


@pytest.mark.asyncio
async def test_run_once_executes_all_scrapers(scheduler):
    """Test that run_once executes all scrapers for a team"""
    team_id = "test-team"
    results = await scheduler.run_once(team_id)

    assert len(results) == 2
    assert "MockScraperA" in results
    assert "MockScraperB" in results
    assert results["MockScraperA"]["team"] == team_id
    assert results["MockScraperB"]["team"] == team_id


@pytest.mark.asyncio
async def test_scrapers_run_in_order(scheduler):
    """Test that scrapers execute in the order they were added"""
    team_id = "test-team"
    execution_order = []

    # Patch scrapers to track execution order
    async def track_scraper_a(*args, **kwargs):
        execution_order.append("A")
        return {"source": "A"}

    async def track_scraper_b(*args, **kwargs):
        execution_order.append("B")
        return {"source": "B"}

    scheduler.scrapers[0].scrape_team = track_scraper_a
    scheduler.scrapers[1].scrape_team = track_scraper_b

    await scheduler.run_once(team_id)

    assert execution_order == ["A", "B"]


@pytest.mark.asyncio
async def test_stop_interrupts_continuous_mode(rate_limiter):
    """Test that stop() interrupts continuous scraping"""
    scrapers = [MockScraperA(rate_limiter)]
    scheduler = ScraperScheduler(scrapers, rate_limiter)

    run_count = 0

    async def count_runs(*args, **kwargs):
        nonlocal run_count
        run_count += 1
        return {"run": run_count}

    scheduler.scrapers[0].scrape_team = count_runs

    # Start continuous mode in background
    task = asyncio.create_task(scheduler.run_continuous(["team1", "team2"], interval_seconds=0.1))

    # Let it run for a bit
    await asyncio.sleep(0.3)

    # Stop it
    scheduler.stop()
    await asyncio.wait_for(task, timeout=1.0)

    # Should have run a few times but not indefinitely
    assert run_count > 0
    assert run_count < 10  # Should stop quickly


@pytest.mark.asyncio
async def test_error_in_one_scraper_doesnt_stop_others(rate_limiter):
    """Test that error in one scraper doesn't prevent others from running"""
    scrapers = [FailingScraper(rate_limiter), MockScraperA(rate_limiter)]
    scheduler = ScraperScheduler(scrapers, rate_limiter)

    results = await scheduler.run_once("test-team")

    # Failing scraper should return None (no result added)
    assert "FailingScraper" not in results
    # But MockScraperA should still run
    assert "MockScraperA" in results
    assert results["MockScraperA"]["team"] == "test-team"


@pytest.mark.asyncio
async def test_close_cleans_up_all_scrapers(scheduler):
    """Test that close() calls close on all scrapers"""
    close_calls = []

    async def track_close(scraper_name):
        close_calls.append(scraper_name)

    scheduler.scrapers[0].close = lambda: track_close("A")
    scheduler.scrapers[1].close = lambda: track_close("B")

    await scheduler.close()

    assert len(close_calls) == 2
    assert "A" in close_calls
    assert "B" in close_calls


@pytest.mark.asyncio
async def test_run_once_with_empty_scrapers_list(rate_limiter):
    """Test run_once with no scrapers configured"""
    scheduler = ScraperScheduler([], rate_limiter)
    results = await scheduler.run_once("test-team")

    assert results == {}


@pytest.mark.asyncio
async def test_continuous_mode_processes_all_teams(rate_limiter):
    """Test that continuous mode processes all team identifiers"""
    scraper = MockScraperA(rate_limiter)
    scheduler = ScraperScheduler([scraper], rate_limiter)

    processed_teams = []

    async def track_teams(team_id):
        processed_teams.append(team_id)
        return {"team": team_id}

    scheduler.scrapers[0].scrape_team = track_teams

    # Run one cycle
    task = asyncio.create_task(
        scheduler.run_continuous(["team1", "team2", "team3"], interval_seconds=0.05)
    )

    # Wait for one full cycle
    await asyncio.sleep(0.3)
    scheduler.stop()
    await asyncio.wait_for(task, timeout=1.0)

    # Should have processed all teams at least once
    assert "team1" in processed_teams
    assert "team2" in processed_teams
    assert "team3" in processed_teams
