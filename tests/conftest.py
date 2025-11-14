"""Pytest configuration and fixtures"""

import pytest
from app.core.config import settings


@pytest.fixture
def test_settings():
    """Test settings fixture"""
    return settings


@pytest.fixture
def sample_law_text():
    """Sample law text for testing"""
    return """
第一条　この法律は、株式会社、合名会社、合資会社及び合同会社の設立、組織、
運営及び管理について定めることを目的とする。

第二条　会社は、この法律の定めるところにより、定款を作成し、本店の所在地に
おいて設立の登記をすることによって成立する。
"""


@pytest.fixture
def sample_case_text():
    """Sample case text for testing"""
    return """
判例要旨：契約違反による損害賠償請求において、債務者の故意または過失が
認められる場合、債権者は損害賠償を請求することができる。

判決全文：本件は、売買契約における債務不履行を理由とする損害賠償請求事件である。
原告は被告に対して、商品の引渡しを求めたが、被告は正当な理由なく引渡しを拒否した。
"""
