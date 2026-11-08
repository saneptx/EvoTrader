"""Shared pytest configuration."""

from __future__ import annotations

from pathlib import Path

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
def clean_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> pytest.MonkeyPatch:
    """Remove EvoTrader variables inherited from the developer shell and run in an empty
    working directory, so neither the shell nor a local ``.env`` leaks into the test."""
    for name in _EVOTRADER_ENV:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.chdir(tmp_path)
    return monkeypatch
