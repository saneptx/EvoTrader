"""Runtime configuration loaded from environment variables (spec §3, §16).

v0.1 supports research mode only: any other ``RUN_MODE`` fails startup.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from evotrader.core.errors import ConfigurationError

SUPPORTED_RUN_MODES = ("research",)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=None,
        case_sensitive=False,
        extra="ignore",
        frozen=True,
    )

    run_mode: Literal["research"] = "research"
    database_url: str = "postgresql+psycopg://evotrader:evotrader@127.0.0.1:5432/evotrader"
    redis_url: str = "redis://127.0.0.1:6379/0"
    artifact_root: Path = Path("./artifacts")

    llm_provider: Literal["fake"] = "fake"
    llm_model: str = "fake-model-v0"
    llm_api_key: SecretStr | None = None
    max_llm_calls: int = Field(default=0, ge=0)
    max_research_cost_usd: Decimal = Field(default=Decimal("0"), ge=0)


def load_settings() -> Settings:
    """Load settings, converting validation failures into a redacted ``ConfigurationError``."""
    try:
        return Settings()
    except ValidationError as exc:
        fields = sorted({".".join(str(p) for p in err["loc"]) for err in exc.errors()})
        # Only field names are reported: input values may contain secrets.
        raise ConfigurationError(
            f"Invalid configuration for: {', '.join(fields)}. "
            f"Supported RUN_MODE values: {', '.join(SUPPORTED_RUN_MODES)}."
        ) from None
