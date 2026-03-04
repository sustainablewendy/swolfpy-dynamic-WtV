import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers to suppress PytestUnknownMarkWarning."""
    config.addinivalue_line(
        "markers",
        "slow: marks tests requiring Premise DB generation (>30s) — skip with '-m not slow'",
    )
