"""Shared fixtures for the compliance test suite."""

from __future__ import annotations

from typing import Dict

import pytest

from dili_compliance.engine import PrevailingRate
from dili_compliance.runner import default_rates


@pytest.fixture(scope="session")
def prevailing_rates() -> Dict[str, PrevailingRate]:
    return default_rates()
