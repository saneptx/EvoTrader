"""Shared pytest configuration."""

from __future__ import annotations

import pytest

_EVOTRADER_ENV = (
    "RUN_MODE",
    "DATABASE_URL",
    "REDIS_URL",
    "ARTIFACT_ROOT",
    "LLM_PROVIDER",
    "LLM_MODEL",
    "LLM_API_KEY",
    "MAX_LLM_CALLS",
    "MAX_RESEARCH_COST_USD",
)


@pytest.fixture
def clean_env(monkeypatch: pytest.MonkeyPatch) -> pytest.MonkeyPatch:
    """Remove EvoTrader variables inherited from the developer shell."""
    for name in _EVOTRADER_ENV:
        monkeypatch.delenv(name, raising=False)
    return monkeypatch
