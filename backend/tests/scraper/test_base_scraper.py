import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.scraper.base import BaseScraper
from app.scraper.rate_limiter import RateLimiter
import httpx


# Mock scraper implementation for testing
class MockScraper(BaseScraper):
    @property
    def domain(self) -> str:
        return "mock.example.com"

    async def scrape_team(self, team_identifier: str):
        return {"team_name": team_identifier}


@pytest.fixture
def rate_limiter():
    return RateLimiter(min_delay_seconds=0)


@pytest.fixture
def mock_scraper(rate_limiter):
    return MockScraper(rate_limiter)


@pytest.mark.asyncio
async def test_base_scraper_initialization(mock_scraper):
    """Test that base scraper initializes correctly"""
    assert mock_scraper.rate_limiter is not None
    assert mock_scraper.client is not None
    assert isinstance(mock_scraper.client, httpx.AsyncClient)


@pytest.mark.asyncio
async def test_fetch_with_rate_limiting(mock_scraper):
    """Test that fetch method calls rate limiter"""
    url = "http://mock.example.com/page"
    mock_html = "<html><body>Test</body></html>"

    with patch.object(mock_scraper.rate_limiter, "wait_if_needed", new_callable=AsyncMock) as mock_wait:
        with patch.object(mock_scraper.client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.text = mock_html
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            result = await mock_scraper.fetch(url)

            # Verify rate limiter was called
            mock_wait.assert_called_once_with(mock_scraper.domain)
            # Verify HTTP request was made
            mock_get.assert_called_once_with(url)
            # Verify result
            assert result == mock_html


@pytest.mark.asyncio
async def test_fetch_handles_http_errors(mock_scraper):
    """Test that fetch handles HTTP errors gracefully"""
    url = "http://mock.example.com/notfound"

    with patch.object(mock_scraper.rate_limiter, "wait_if_needed", new_callable=AsyncMock):
        with patch.object(mock_scraper.client, "get") as mock_get:
            mock_get.side_effect = httpx.HTTPStatusError(
                "404 Not Found", request=MagicMock(), response=MagicMock()
            )

            result = await mock_scraper.fetch(url)

            # Should return None on error
            assert result is None


@pytest.mark.asyncio
async def test_fetch_handles_network_errors(mock_scraper):
    """Test that fetch handles network errors gracefully"""
    url = "http://mock.example.com/page"

    with patch.object(mock_scraper.rate_limiter, "wait_if_needed", new_callable=AsyncMock):
        with patch.object(mock_scraper.client, "get") as mock_get:
            mock_get.side_effect = httpx.NetworkError("Connection failed")

            result = await mock_scraper.fetch(url)

            # Should return None on network error
            assert result is None


@pytest.mark.asyncio
async def test_user_agent_header_is_set(rate_limiter):
    """Test that User-Agent header is set correctly"""
    scraper = MockScraper(rate_limiter)

    assert "User-Agent" in scraper.client.headers
    assert "CyclingLineageBot" in scraper.client.headers["User-Agent"]


@pytest.mark.asyncio
async def test_scraper_close_cleans_up(mock_scraper):
    """Test that close method cleans up resources"""
    with patch.object(mock_scraper.client, "aclose", new_callable=AsyncMock) as mock_close:
        await mock_scraper.close()
        mock_close.assert_called_once()


@pytest.mark.asyncio
async def test_scrape_team_abstract_method(mock_scraper):
    """Test that scrape_team is implemented in subclass"""
    result = await mock_scraper.scrape_team("test-team")
    assert result == {"team_name": "test-team"}
