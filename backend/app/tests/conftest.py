"""Expose shared fixtures from the main test suite to app-level tests."""

# Re-export fixtures so pytest can find them for this subtree.
from tests.conftest import *  # noqa: F401,F403
