"""Error hierarchy with stable, machine-readable error codes."""

from __future__ import annotations


class EvoTraderError(Exception):
    """Base class for all domain errors. ``code`` is part of the public API contract."""

    code: str = "EVOTRADER_ERROR"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ConfigurationError(EvoTraderError):
    """Invalid or unsafe runtime configuration; the process must not start."""

    code = "CONFIGURATION_ERROR"
