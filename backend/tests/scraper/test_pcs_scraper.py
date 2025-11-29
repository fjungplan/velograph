"""Tests for ProCyclingStats scraper."""
import pytest
from pathlib import Path

from app.scraper.parsers.pcs_scraper import PCScraper
from app.scraper.rate_limiter import RateLimiter


# Fixture directory
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "pcs"


@pytest.fixture
def pcs_scraper():
    """Create PCScraper instance for testing."""
    rate_limiter = RateLimiter()
    return PCScraper(rate_limiter=rate_limiter)


def load_fixture(filename: str) -> str:
    """Load HTML fixture file."""
    filepath = FIXTURES_DIR / filename
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


class TestPCScraper:
    """Tests for PCScraper parsing methods."""
    
    def test_parse_worldteam(self, pcs_scraper):
        """Test parsing WorldTeam page."""
        html = load_fixture("team_worldtour.html")
        data = pcs_scraper.parse_team_page(html)
        
        assert data is not None
        assert data.source == "procyclingstats"
        assert data.team_name == "Team Visma | Lease a Bike"
        assert data.uci_code == "TVL"
        assert data.tier == "WT"
        assert len(data.sponsors) > 0
    
    def test_parse_proteam(self, pcs_scraper):
        """Test parsing ProTeam page."""
        html = load_fixture("team_proteam.html")
        data = pcs_scraper.parse_team_page(html)
        
        assert data is not None
        assert data.team_name == "TotalEnergies"
        assert data.uci_code == "TEN"
        assert data.tier == "PT"
    
    def test_parse_continental(self, pcs_scraper):
        """Test parsing Continental team page."""
        html = load_fixture("team_continental.html")
        data = pcs_scraper.parse_team_page(html)
        
        assert data is not None
        assert data.team_name == "Intermarché - Circus - Wanty"
        assert data.tier == "CT"
    
    def test_extract_team_name(self, pcs_scraper):
        """Test team name extraction."""
        html = load_fixture("team_with_uci_code.html")
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        name = pcs_scraper._extract_team_name(soup)
        assert name == "UAE Team Emirates"
    
    def test_extract_uci_code(self, pcs_scraper):
        """Test UCI code extraction."""
        html = load_fixture("team_with_uci_code.html")
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        code = pcs_scraper._extract_uci_code(soup)
        assert code == "UAD"
    
    def test_extract_uci_code_missing(self, pcs_scraper):
        """Test UCI code extraction when missing."""
        html = load_fixture("team_continental.html")
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        code = pcs_scraper._extract_uci_code(soup)
        assert code is None
    
    def test_extract_tier_worldteam(self, pcs_scraper):
        """Test tier extraction for WorldTeam."""
        html = load_fixture("team_worldtour.html")
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        tier = pcs_scraper._extract_tier(soup)
        assert tier == "WT"
    
    def test_extract_tier_proteam(self, pcs_scraper):
        """Test tier extraction for ProTeam."""
        html = load_fixture("team_proteam.html")
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        tier = pcs_scraper._extract_tier(soup)
        assert tier == "PT"
    
    def test_extract_tier_continental(self, pcs_scraper):
        """Test tier extraction for Continental team."""
        html = load_fixture("team_continental.html")
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        tier = pcs_scraper._extract_tier(soup)
        assert tier == "CT"
    
    def test_extract_sponsors(self, pcs_scraper):
        """Test sponsor extraction from team name."""
        sponsors = pcs_scraper._extract_sponsors("Team Visma | Lease a Bike")
        
        # Sponsor extraction splits on delimiters
        assert "Team Visma" in sponsors
        assert "Lease a Bike" in sponsors
        assert len(sponsors) == 2
    
    def test_extract_sponsors_with_dashes(self, pcs_scraper):
        """Test sponsor extraction with dash delimiters."""
        sponsors = pcs_scraper._extract_sponsors("Intermarché - Circus - Wanty")
        
        assert "Intermarché" in sponsors
        assert "Circus" in sponsors
        assert "Wanty" in sponsors
    
    def test_parse_invalid_html(self, pcs_scraper):
        """Test parsing with invalid/incomplete HTML."""
        html = "<html><body><p>No h1 tag</p></body></html>"
        data = pcs_scraper.parse_team_page(html)
        
        # Should return None if team_name extraction fails
        assert data is None
    
    def test_parse_empty_html(self, pcs_scraper):
        """Test parsing with empty HTML."""
        data = pcs_scraper.parse_team_page("")
        assert data is None


@pytest.mark.asyncio
async def test_scrape_team_integration(pcs_scraper, monkeypatch):
    """Test full scrape_team workflow with mocked fetch."""
    html = load_fixture("team_worldtour.html")
    
    # Mock fetch method
    async def mock_fetch(url):
        return html
    
    monkeypatch.setattr(pcs_scraper, 'fetch', mock_fetch)
    
    result = await pcs_scraper.scrape_team("team-visma-lease-a-bike-2024")
    
    assert result.success is True
    assert result.error is None
    assert result.data is not None
    assert result.data.team_name == "Team Visma | Lease a Bike"


@pytest.mark.asyncio
async def test_scrape_team_fetch_failure(pcs_scraper, monkeypatch):
    """Test scrape_team with fetch failure."""
    
    # Mock fetch to return None
    async def mock_fetch(url):
        return None
    
    monkeypatch.setattr(pcs_scraper, 'fetch', mock_fetch)
    
    result = await pcs_scraper.scrape_team("invalid-team")
    
    assert result.success is False
    assert result.error is not None
    assert result.data is None


@pytest.mark.asyncio
async def test_scrape_team_parse_failure(pcs_scraper, monkeypatch):
    """Test scrape_team with parse failure."""
    
    # Mock fetch to return invalid HTML
    async def mock_fetch(url):
        return "<html><body></body></html>"
    
    monkeypatch.setattr(pcs_scraper, 'fetch', mock_fetch)
    
    result = await pcs_scraper.scrape_team("team-invalid")
    
    assert result.success is False
    assert "Failed to parse" in result.error
    assert result.data is None
