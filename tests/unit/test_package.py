from __future__ import annotations

import ast
import importlib
from pathlib import Path

import pytest

import evotrader

pytestmark = pytest.mark.unit

SRC = Path(evotrader.__file__).parent
SPEC_MODULES = ("api", "core", "data", "dsl", "backtest", "research", "memory", "agents", "workers")
DETERMINISTIC = ("core", "data", "dsl", "backtest")
FORBIDDEN_FOR_DETERMINISTIC = ("evotrader.agents", "evotrader.memory", "evotrader.api")


def test_version() -> None:
    assert evotrader.__version__ == "0.1.0"


@pytest.mark.parametrize("name", SPEC_MODULES)
def test_spec_modules_importable(name: str) -> None:
    importlib.import_module(f"evotrader.{name}")


def _imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


@pytest.mark.parametrize("package", DETERMINISTIC)
def test_deterministic_modules_do_not_import_agents(package: str) -> None:
    """ADR-0001: the deterministic core must not depend on LLM/memory/API layers."""
    for path in (SRC / package).rglob("*.py"):
        for mod in _imported_modules(path):
            assert not mod.startswith(FORBIDDEN_FOR_DETERMINISTIC), f"{path} imports {mod}"


def test_no_dynamic_code_evaluation_in_source() -> None:
    """Spec §0.7: no eval/exec anywhere in the package."""
    for path in SRC.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                assert node.func.id not in {"eval", "exec", "compile"}, f"{path}: {node.func.id}"
