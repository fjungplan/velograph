import pytest
import asyncio
from datetime import datetime
from app.scraper.rate_limiter import RateLimiter


@pytest.mark.asyncio
async def test_rate_limiter_enforces_delay():
    """Test that rate limiter enforces minimum delay between requests"""
    limiter = RateLimiter(min_delay_seconds=1)
    domain = "example.com"

    start_time = datetime.now()
    await limiter.wait_if_needed(domain)
    first_request = datetime.now()

    # Second request should be delayed
    await limiter.wait_if_needed(domain)
    second_request = datetime.now()

    elapsed = (second_request - first_request).total_seconds()
    assert elapsed >= 1.0, f"Expected delay >= 1.0s, got {elapsed}s"


@pytest.mark.asyncio
async def test_rate_limiter_multiple_domains():
    """Test that multiple domains are tracked independently"""
    limiter = RateLimiter(min_delay_seconds=1)

    # Request to domain1
    await limiter.wait_if_needed("domain1.com")
    time1 = datetime.now()

    # Immediate request to domain2 should not be delayed
    await limiter.wait_if_needed("domain2.com")
    time2 = datetime.now()

    elapsed = (time2 - time1).total_seconds()
    assert elapsed < 0.1, f"Expected no delay between different domains, got {elapsed}s"


@pytest.mark.asyncio
async def test_rate_limiter_concurrent_requests_serialized():
    """Test that concurrent requests to same domain are serialized"""
    limiter = RateLimiter(min_delay_seconds=0.5)
    domain = "example.com"
    results = []

    async def make_request(request_id: int):
        await limiter.wait_if_needed(domain)
        results.append((request_id, datetime.now()))

    # Fire 3 concurrent requests
    await asyncio.gather(
        make_request(1),
        make_request(2),
        make_request(3),
    )

    # Verify they were serialized (each ~0.5s apart)
    assert len(results) == 3
    time_diffs = [
        (results[i + 1][1] - results[i][1]).total_seconds() for i in range(len(results) - 1)
    ]
    for diff in time_diffs:
        assert diff >= 0.5, f"Expected delay >= 0.5s between requests, got {diff}s"


@pytest.mark.asyncio
async def test_rate_limiter_no_delay_first_request():
    """Test that first request to a domain has no delay"""
    limiter = RateLimiter(min_delay_seconds=2)
    domain = "newdomain.com"

    start = datetime.now()
    await limiter.wait_if_needed(domain)
    end = datetime.now()

    elapsed = (end - start).total_seconds()
    assert elapsed < 0.1, f"Expected no delay for first request, got {elapsed}s"


@pytest.mark.asyncio
async def test_rate_limiter_custom_delay():
    """Test rate limiter with custom delay setting"""
    custom_delay = 2
    limiter = RateLimiter(min_delay_seconds=custom_delay)
    domain = "example.com"

    await limiter.wait_if_needed(domain)
    start = datetime.now()
    await limiter.wait_if_needed(domain)
    end = datetime.now()

    elapsed = (end - start).total_seconds()
    assert elapsed >= custom_delay, f"Expected delay >= {custom_delay}s, got {elapsed}s"
