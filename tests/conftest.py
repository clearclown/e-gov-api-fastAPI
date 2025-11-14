"""
pytest設定ファイル

全テストで共有されるフィクスチャと設定を定義します。
"""

import pytest
import asyncio
from typing import Generator


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """イベントループのフィクスチャ

    全テストセッションで共有されるイベントループを提供します。
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def disable_cache():
    """テスト時にキャッシュを無効化

    環境変数を設定してRedisキャッシュを無効にします。
    """
    import os
    os.environ["REDIS_ENABLED"] = "false"
    yield
    os.environ.pop("REDIS_ENABLED", None)


@pytest.fixture
def mock_law_data():
    """テスト用の法令データ"""
    return {
        "law_id": "405AC0000000087",
        "law_number": "平成十七年法律第八十七号",
        "law_name": "会社法",
        "law_type": "法律",
        "promulgation_date": "2005-07-26",
        "enforcement_date": "2006-05-01",
        "full_text": "会社法の全文テキスト...",
        "toc": [
            {
                "chapter": "第一章",
                "title": "総則",
                "articles": ["1", "2", "3"]
            }
        ],
        "metadata": {
            "source": "e-gov"
        }
    }
