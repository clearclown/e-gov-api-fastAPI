"""pytest configuration and fixtures"""

import pytest


@pytest.fixture(scope="session")
def test_config():
    """テスト用の設定"""
    return {
        "test_user_id": "test_user_12345",
        "test_law_id": "405AC0000000087",
        "test_case_id": "CASE-2024-001",
    }
