# cache.py
"""Caching utilities for the Crystal Visualizer.

Provides a thin wrapper around ``functools.lru_cache`` that respects the
``CACHE_MAXSIZE`` setting from ``config`` and works with Streamlit's session
state.
"""

import functools
from config import CACHE_MAXSIZE


def cached(func):
    """Decorator that applies an LRU cache with a project‑wide size limit.

    The wrapper is transparent to Streamlit – cached results survive across
    reruns as long as the input arguments are identical.
    """
    return functools.lru_cache(maxsize=CACHE_MAXSIZE)(func)
