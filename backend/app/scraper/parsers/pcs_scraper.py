"""ProCyclingStats scraper implementation."""
import re
from typing import Optional
from bs4 import BeautifulSoup

from ..base import BaseScraper
from ..models import ScrapedTeamData, ScraperResult


class PCScraper(BaseScraper):
    """Scraper for ProCyclingStats.com."""
    
    BASE_URL = "https://www.procyclingstats.com"
    
    @property
    def domain(self) -> str:
        """Return domain for rate limiting."""
        return "procyclingstats.com"
    
    async def scrape_team(self, team_identifier: str) -> ScraperResult:
        """
        Scrape team data from ProCyclingStats.
        
        Args:
            team_identifier: Team slug or UCI code (e.g., 'team-visma-lease-a-bike-2024' or 'TVL')
        
        Returns:
            ScraperResult with success status and optional data
        """
        try:
            # Construct URL
            url = f"{self.BASE_URL}/team/{team_identifier}"
            
            # Fetch HTML
            html = await self.fetch(url)
            if not html:
                return ScraperResult(
                    success=False,
                    error=f"Failed to fetch {url}",
                    data=None
                )
            
            # Parse HTML
            data = self.parse_team_page(html)
            if not data:
                return ScraperResult(
                    success=False,
                    error="Failed to parse team page",
                    data=None
                )
            
            return ScraperResult(success=True, data=data)
            
        except Exception as e:
            return ScraperResult(
                success=False,
                error=str(e),
                data=None
            )
    
    def parse_team_page(self, html: str) -> Optional[ScrapedTeamData]:
        """
        Parse team page HTML and extract structured data.
        
        Args:
            html: Raw HTML content
        
        Returns:
            ScrapedTeamData or None if parsing fails
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract fields
            team_name = self._extract_team_name(soup)
            if not team_name:
                return None
            
            uci_code = self._extract_uci_code(soup)
            tier = self._extract_tier(soup)
            sponsors = self._extract_sponsors(team_name)
            
            return ScrapedTeamData(
                source="procyclingstats",
                team_name=team_name,
                uci_code=uci_code,
                tier=tier,
                sponsors=sponsors
            )
            
        except Exception:
            return None
    
    def _extract_team_name(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extract team name from h1 tag.
        
        Args:
            soup: BeautifulSoup parsed HTML
        
        Returns:
            Team name or None
        """
        h1 = soup.find('h1')
        if h1:
            return h1.get_text(strip=True)
        return None
    
    def _extract_uci_code(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extract UCI code using regex pattern.
        
        Looks for patterns like "UCI Code: ABC" in the page text.
        
        Args:
            soup: BeautifulSoup parsed HTML
        
        Returns:
            3-letter UCI code or None
        """
        text = soup.get_text()
        match = re.search(r'UCI Code:\s*([A-Z]{3})', text, re.IGNORECASE)
        if match:
            return match.group(1).upper()
        return None
    
    def _extract_tier(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extract team tier from page content.
        
        Looks for indicators like "UCI WorldTeam", "UCI ProTeam", etc.
        
        Args:
            soup: BeautifulSoup parsed HTML
        
        Returns:
            Tier string ("WT", "PT", "CT") or None
        """
        text = soup.get_text().lower()
        
        if 'worldteam' in text or 'world team' in text:
            return 'WT'
        elif 'proteam' in text or 'pro team' in text:
            return 'PT'
        elif 'continental' in text:
            return 'CT'
        
        return None
    
    def _extract_sponsors(self, team_name: str) -> list[str]:
        """
        Extract sponsor names from team name by splitting on delimiters.
        
        Splits on common delimiters: -, |, /, and extracts sponsor names.
        
        Args:
            team_name: Full team name potentially containing sponsor names
        
        Returns:
            List of sponsor names
        """
        if not team_name:
            return []
        
        # Split on common delimiters
        delimiters = ['-', '|', '/']
        parts = [team_name]
        
        for delimiter in delimiters:
            new_parts = []
            for part in parts:
                new_parts.extend(part.split(delimiter))
            parts = new_parts
        
        # Clean and filter
        sponsors = []
        for part in parts:
            part = part.strip()
            # Skip common non-sponsor terms
            if part and part.lower() not in ['team', 'cycling', 'racing']:
                sponsors.append(part)
        
        return sponsors
