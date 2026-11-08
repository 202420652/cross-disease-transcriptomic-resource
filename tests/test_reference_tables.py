"""Run the reference-table consistency checks as a pytest test."""

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_validator():
    spec = importlib.util.spec_from_file_location(
        "validate_reference_tables",
        REPO_ROOT / "scripts" / "validate_reference_tables.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_reference_tables_are_consistent():
    validator = _load_validator()
    failures = validator.collect_failures(REPO_ROOT / "data" / "reference")
    assert failures == [], "reference-table inconsistencies: " + "; ".join(failures)
