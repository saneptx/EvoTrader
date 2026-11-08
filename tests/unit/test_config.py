from __future__ import annotations

import shutil
from decimal import Decimal
from pathlib import Path

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


# --- .env file contract (README "Configuration"; Day 1 acceptance follow-up) ---

REPO_ROOT = Path(__file__).resolve().parents[2]


def _write_env(lines: list[str]) -> None:
    Path(".env").write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_dotenv_in_working_directory_is_applied(clean_env: pytest.MonkeyPatch) -> None:
    _write_env(["RUN_MODE=research", "ARTIFACT_ROOT=/tmp/evo-dotenv-sentinel"])
    settings = load_settings()
    assert settings.artifact_root == Path("/tmp/evo-dotenv-sentinel")  # noqa: S108


def test_dotenv_live_run_mode_fails_startup(clean_env: pytest.MonkeyPatch) -> None:
    _write_env(["RUN_MODE=live", "ARTIFACT_ROOT=/tmp/evo-dotenv-sentinel"])
    with pytest.raises(ConfigurationError) as info:
        load_settings()
    assert "run_mode" in info.value.message


def test_process_env_overrides_dotenv(clean_env: pytest.MonkeyPatch) -> None:
    _write_env(["ARTIFACT_ROOT=/tmp/from-dotenv"])
    clean_env.setenv("ARTIFACT_ROOT", "/tmp/from-process")  # noqa: S108
    assert load_settings().artifact_root == Path("/tmp/from-process")  # noqa: S108


def test_process_env_cannot_be_bypassed_by_dotenv_research(clean_env: pytest.MonkeyPatch) -> None:
    _write_env(["RUN_MODE=research"])
    clean_env.setenv("RUN_MODE", "live")
    with pytest.raises(ConfigurationError):
        load_settings()


def test_env_example_copied_verbatim_loads_as_research(clean_env: pytest.MonkeyPatch) -> None:
    """``cp .env.example .env`` must yield a valid research configuration (compose keys ignored)."""
    shutil.copyfile(REPO_ROOT / ".env.example", ".env")
    settings = load_settings()
    assert settings.run_mode == "research"
    assert settings.artifact_root == Path("artifacts")
    assert settings.llm_provider == "fake"
