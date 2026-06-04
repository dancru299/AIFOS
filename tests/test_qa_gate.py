"""Unit tests for the deterministic QA gate (app.services.qa.gate)."""

import json

from app.services.qa.gate import run_quality_gate


def test_gate_passes_on_valid_python(tmp_path):
    (tmp_path / "main.py").write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")

    result = run_quality_gate(tmp_path, timeout=30)

    assert result.passed
    assert any(c.name == "python_compile" and c.status == "passed" for c in result.checks)


def test_gate_fails_on_python_syntax_error(tmp_path):
    # Missing colon -> py_compile fails regardless of whether ruff is installed.
    (tmp_path / "broken.py").write_text("def add(a, b)\n    return a + b\n", encoding="utf-8")

    result = run_quality_gate(tmp_path, timeout=30)

    assert not result.passed
    assert any(c.name == "python_compile" and c.failed for c in result.checks)
    assert result.failures


def test_gate_skips_when_nothing_to_check(tmp_path):
    (tmp_path / "notes.md").write_text("# Just prose, no code\n", encoding="utf-8")

    result = run_quality_gate(tmp_path, timeout=30)

    assert result.passed
    assert any(c.name == "no_automated_checks" and c.status == "skipped" for c in result.checks)


def test_gate_skips_node_build_without_node_modules(tmp_path):
    # A build script but no installed deps: skipped, not failed (no network in QA).
    (tmp_path / "package.json").write_text(
        json.dumps({"name": "x", "scripts": {"build": "tsc"}}), encoding="utf-8"
    )

    result = run_quality_gate(tmp_path, timeout=30)

    assert result.passed
    assert any(c.name == "node_build" and c.status == "skipped" for c in result.checks)


def test_gate_ignores_vendor_dirs(tmp_path):
    # Broken code inside node_modules / venv must not fail the gate.
    vendor = tmp_path / "node_modules" / "pkg"
    vendor.mkdir(parents=True)
    (vendor / "bad.py").write_text("def broken(\n", encoding="utf-8")
    (tmp_path / "ok.py").write_text("x = 1\n", encoding="utf-8")

    result = run_quality_gate(tmp_path, timeout=30)

    assert result.passed
