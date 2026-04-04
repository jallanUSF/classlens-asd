"""
ClassLens ASD Testing Module

Provides mock API clients, fixtures, and test utilities for offline development
and testing of the ClassLens pipeline without requiring API keys or rate limits.
"""

from tests.mock_api_responses import MockGemmaClient

__all__ = ["MockGemmaClient"]
