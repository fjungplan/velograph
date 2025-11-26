"""
Pytest configuration and fixtures.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient
from typing import AsyncGenerator
from main import app


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """
    Create an async test client for FastAPI app.
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
