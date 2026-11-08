from __future__ import annotations

from decimal import Decimal

import pytest

from evotrader.core.config import load_settings
from evotrader.core.errors import ConfigurationError

pytestmark = pytest.mark.unit


def test_defaults_are_research_mode_without_secrets(clean_env: pytest.MonkeyPatch) -> None:
    settings = load_settings()
    assert settings.run_mode == "research"
    assert settings.llm_provider == "fake"
    assert settings.llm_api_key is None
    assert settings.max_llm_calls == 0
    assert settings.max_research_cost_usd == Decimal("0")


@pytest.mark.parametrize("mode", ["live", "LIVE", "paper", "production", ""])
def test_non_research_run_mode_fails_startup(clean_env: pytest.MonkeyPatch, mode: str) -> None:
    clean_env.setenv("RUN_MODE", mode)
    with pytest.raises(ConfigurationError) as info:
        load_settings()
    assert info.value.code == "CONFIGURATION_ERROR"
    assert "run_mode" in info.value.message


def test_env_overrides_are_applied(clean_env: pytest.MonkeyPatch) -> None:
    clean_env.setenv("ARTIFACT_ROOT", "/tmp/evotrader-artifacts")  # noqa: S108
    clean_env.setenv("MAX_LLM_CALLS", "5")
    settings = load_settings()
    assert str(settings.artifact_root) == "/tmp/evotrader-artifacts"  # noqa: S108
    assert settings.max_llm_calls == 5


def test_api_key_is_never_rendered(clean_env: pytest.MonkeyPatch) -> None:
    clean_env.setenv("LLM_API_KEY", "sk-test-not-a-real-key")
    settings = load_settings()
    assert "sk-test-not-a-real-key" not in repr(settings)
    assert "sk-test-not-a-real-key" not in str(settings.model_dump())


def test_invalid_values_do_not_leak_into_error_message(clean_env: pytest.MonkeyPatch) -> None:
    clean_env.setenv("MAX_LLM_CALLS", "secret-looking-value")
    with pytest.raises(ConfigurationError) as info:
        load_settings()
    assert "secret-looking-value" not in info.value.message
    assert "max_llm_calls" in info.value.message


def test_negative_budget_rejected(clean_env: pytest.MonkeyPatch) -> None:
    clean_env.setenv("MAX_RESEARCH_COST_USD", "-1")
    with pytest.raises(ConfigurationError):
        load_settings()
