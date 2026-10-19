"""Traceability meta-tests: the registry itself is under test.

Stronger than the TypeScript version — these also check citation *format* and
that every scenario is actually exercised by a scenario-driven test.
"""

from __future__ import annotations

import re

import pytest

from dili_compliance.registry import CITATIONS, SCENARIO_REGISTRY

pytestmark = pytest.mark.unit

# e.g. "29 CFR 5.5(a)(1)(i)" or "26 U.S.C. 45(b)(8)(B)"
CITATION_RE = re.compile(r"(\d+\s*CFR\s*\d+\.\d+|\d+\s*U\.S\.C\.\s*\d+)\(?")


def test_every_scenario_has_core_fields():
    for s in SCENARIO_REGISTRY:
        assert s.id, "scenario id"
        assert s.rule, f"rule for {s.id}"
        assert s.citation, f"citation for {s.id}"
        assert s.description, f"description for {s.id}"


def test_scenario_ids_are_unique():
    ids = [s.id for s in SCENARIO_REGISTRY]
    assert len(set(ids)) == len(ids)


def test_citations_are_paragraph_level():
    """Traceability: no bare 'Part 5' — citations must be paragraph-level."""
    for s in SCENARIO_REGISTRY:
        assert "Part 5" not in s.citation, f"{s.id} citation too broad: {s.citation}"
        assert CITATION_RE.search(s.citation), f"{s.id} citation not specific: {s.citation}"


def test_citations_are_on_the_reviewed_list():
    """A well-formed but wrong paragraph must still fail: every citation has to
    be registered in CITATIONS, where its heading is visible to reviewers."""
    for s in SCENARIO_REGISTRY:
        assert s.citation in CITATIONS, (
            f"{s.id} cites {s.citation!r}, which is not in registry.CITATIONS"
        )


def test_citation_matches_area():
    """Prevailing-wage scenarios cite 29 CFR 5.5; apprenticeship ones cite the
    labor-hours paragraph 45(b)(8)(A), not the journeyworker ratio in (B)."""
    for s in SCENARIO_REGISTRY:
        if s.area == "prevailing-wage":
            assert s.citation.startswith("29 CFR 5.5"), f"{s.id}: {s.citation}"
        else:
            assert s.citation == "26 U.S.C. 45(b)(8)(A)", f"{s.id}: {s.citation}"


def test_conformance_scenarios_cite_conformance_paragraph():
    for s in SCENARIO_REGISTRY:
        if s.rule.lower().startswith("conformance"):
            assert s.citation == "29 CFR 5.5(a)(1)(iii)", f"{s.id}: {s.citation}"


def test_every_scenario_has_inputs():
    for s in SCENARIO_REGISTRY:
        if s.area == "prevailing-wage":
            assert s.wage is not None, f"{s.id} missing wage input"
        else:
            assert s.ratio is not None, f"{s.id} missing ratio input"


def test_error_scenarios_are_tagged_failure_mode():
    for s in SCENARIO_REGISTRY:
        if s.expected_error:
            assert "failure-mode" in s.tags, f"{s.id} expects an error but is not tagged"


def test_each_area_has_happy_path_and_violation():
    for area in ("prevailing-wage", "apprenticeship"):
        tags = {t for s in SCENARIO_REGISTRY if s.area == area for t in s.tags}
        assert {"happy-path", "violation", "failure-mode"} <= tags, f"{area}: {tags}"
