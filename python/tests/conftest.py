"""Shared fixtures and the end-of-run compliance result table."""

from __future__ import annotations

from typing import Dict

import pytest

from dili_compliance.engine import PrevailingRate
from dili_compliance.registry import SCENARIO_REGISTRY
from dili_compliance.runner import default_rates


@pytest.fixture(scope="session")
def prevailing_rates() -> Dict[str, PrevailingRate]:
    return default_rates()


# --- end-of-run compliance result table -----------------------------------
# Per-scenario pass/fail, printed after pytest's own summary so each release has
# a readable scenario -> citation -> expected -> result record.

_SCENARIO_OUTCOMES: Dict[str, str] = {}


def pytest_runtest_logreport(report):
    """Record the outcome of each scenario test by its parametrized node id."""
    if report.when == "call":
        _SCENARIO_OUTCOMES[report.nodeid] = report.outcome
    elif report.when == "setup" and report.outcome == "skipped":
        _SCENARIO_OUTCOMES.setdefault(report.nodeid, "skipped")


def _expected_label(scenario) -> str:
    if scenario.expected_error:
        return f"raises {scenario.expected_error}"
    return "compliant" if scenario.expected_compliant else "non-compliant"


def _result_for(scenario) -> str:
    marker = f"[{scenario.id}]"
    outcomes = {o for nid, o in _SCENARIO_OUTCOMES.items() if marker in nid}
    if not outcomes:
        return "–"
    if "failed" in outcomes:
        return "FAIL"
    if outcomes == {"skipped"}:
        return "skip"
    return "PASS"


def pytest_terminal_summary(terminalreporter):
    rows = [(s, _result_for(s)) for s in SCENARIO_REGISTRY]
    if all(result == "–" for _, result in rows):
        return  # scenario tests were deselected (e.g. -m property); skip the table

    headers = ("Scenario", "Area", "Citation", "Expected", "Result")
    table = [
        (s.id, s.area, s.citation, _expected_label(s), result) for s, result in rows
    ]
    widths = [
        max(len(headers[i]), *(len(row[i]) for row in table)) for i in range(len(headers))
    ]

    def fmt(cells):
        return "  ".join(str(c).ljust(widths[i]) for i, c in enumerate(cells))

    tr = terminalreporter
    tr.write_sep("=", "compliance scenario results")
    tr.write_line(fmt(headers))
    tr.write_line("  ".join("-" * w for w in widths))
    for row in table:
        tr.write_line(fmt(row))

    passed = sum(1 for _, result in rows if result == "PASS")
    failed = sum(1 for _, result in rows if result == "FAIL")
    tr.write_line("")
    tr.write_line(
        f"{passed} compliant-as-expected, {failed} failed, {len(rows)} scenarios total"
    )
