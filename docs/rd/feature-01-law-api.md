# 機能仕様書: 法令API（Phase 1）

**機能ID**: FEAT-001
**担当者**: ［担当者名］
**作成日**: 2025-11-14
**ステータス**: 未着手

## 1. 機能概要

e-gov法令APIと連携し、日本国内の法令データを検索・取得する機能を提供する。

## 2. 対象要件

- FR-001: e-gov法令APIとの連携
- FR-002: 法令改正履歴管理
- FR-003: 法令データキャッシング
- FR-007: 法令検索API
- FR-008: 法令詳細取得API
- FR-009: 法令改正履歴API

## 3. 詳細仕様

### 3.1 e-gov APIクライアント

#### 3.1.1 クラス構成

```python
# app/services/egov_client.py

class EGovAPIClient:
    """e-gov法令APIクライアント"""

    def __init__(self, base_url: str, timeout: int = 30):
        """
        Args:
            base_url: e-gov APIのベースURL
            timeout: タイムアウト秒数
        """

    async def search_laws(
        self,
        query: str,
        law_type: Optional[str] = None,
        limit: int = 50
    ) -> List[LawSearchResult]:
        """法令検索"""

    async def get_law_detail(self, law_id: str) -> LawDetail:
        """法令詳細取得"""

    async def get_law_history(self, law_id: str) -> List[LawAmendment]:
        """法令改正履歴取得"""
```

#### 3.1.2 データモデル

```python
# app/models/law.py

from pydantic import BaseModel
from datetime import date
from typing import Optional, List

class LawSearchResult(BaseModel):
    """法令検索結果"""
    law_id: str
    law_number: str  # 法令番号（例: 平成十七年法律第八十七号）
    law_name: str    # 法令名
    law_type: str    # 法令種別（法律、政令、省令など）
    promulgation_date: date  # 公布日
    enforcement_date: Optional[date]  # 施行日

class LawDetail(BaseModel):
    """法令詳細"""
    law_id: str
    law_number: str
    law_name: str
    law_type: str
    promulgation_date: date
    enforcement_date: Optional[date]
    full_text: str  # 全文
    toc: List[dict]  # 目次構造
    metadata: dict

class LawAmendment(BaseModel):
    """法令改正情報"""
    amendment_id: str
    law_id: str
    amendment_law_number: str  # 改正法令番号
    amendment_date: date
    enforcement_date: Optional[date]
    summary: str  # 改正概要
```

### 3.2 REST API エンドポイント

#### 3.2.1 法令検索API

**エンドポイント**: `GET /api/v1/laws/search`

**リクエストパラメータ**:
```
q: str (required) - 検索キーワード
type: str (optional) - 法令種別（law, ordinance, ministerial_order）
limit: int (optional, default=50, max=100) - 取得件数
offset: int (optional, default=0) - オフセット
```

**レスポンス例**:
```json
{
  "total": 125,
  "limit": 50,
  "offset": 0,
  "results": [
    {
      "law_id": "405AC0000000087",
      "law_number": "平成十七年法律第八十七号",
      "law_name": "会社法",
      "law_type": "法律",
      "promulgation_date": "2005-07-26",
      "enforcement_date": "2006-05-01"
    }
  ]
}
```

**実装**:
```python
# app/api/endpoints/laws.py

from fastapi import APIRouter, Query, HTTPException
from typing import Optional

router = APIRouter(prefix="/api/v1/laws", tags=["laws"])

@router.get("/search")
async def search_laws(
    q: str = Query(..., description="検索キーワード"),
    type: Optional[str] = Query(None, description="法令種別"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """法令検索API"""
    # 実装詳細
```

#### 3.2.2 法令詳細取得API

**エンドポイント**: `GET /api/v1/laws/{law_id}`

**パスパラメータ**:
```
law_id: str - 法令ID
```

**クエリパラメータ**:
```
format: str (optional, default=json) - レスポンス形式（json, xml）
```

**レスポンス例**:
```json
{
  "law_id": "405AC0000000087",
  "law_number": "平成十七年法律第八十七号",
  "law_name": "会社法",
  "law_type": "法律",
  "promulgation_date": "2005-07-26",
  "enforcement_date": "2006-05-01",
  "full_text": "（全文テキスト）",
  "toc": [
    {"chapter": "第一章", "title": "総則", "articles": ["1", "2", "3"]}
  ],
  "metadata": {
    "last_updated": "2024-06-15"
  }
}
```

#### 3.2.3 法令改正履歴API

**エンドポイント**: `GET /api/v1/laws/{law_id}/history`

**パスパラメータ**:
```
law_id: str - 法令ID
```

**レスポンス例**:
```json
{
  "law_id": "405AC0000000087",
  "law_name": "会社法",
  "amendments": [
    {
      "amendment_id": "令和元年法律第70号",
      "amendment_law_number": "令和元年法律第七十号",
      "amendment_date": "2019-12-11",
      "enforcement_date": "2021-03-01",
      "summary": "株主総会資料の電子提供制度の創設等"
    }
  ]
}
```

### 3.3 キャッシング戦略

#### 3.3.1 Redis キャッシュ構成

```python
# app/core/cache.py

from redis import asyncio as aioredis
from typing import Optional
import json

class LawCache:
    """法令データキャッシュ"""

    def __init__(self, redis_url: str):
        self.redis = aioredis.from_url(redis_url)

    async def get_law(self, law_id: str) -> Optional[dict]:
        """キャッシュから法令取得"""
        data = await self.redis.get(f"law:{law_id}")
        return json.loads(data) if data else None

    async def set_law(self, law_id: str, data: dict, ttl: int = 86400):
        """法令をキャッシュに保存（デフォルト24時間）"""
        await self.redis.setex(
            f"law:{law_id}",
            ttl,
            json.dumps(data, ensure_ascii=False)
        )

    async def get_search_results(self, cache_key: str) -> Optional[list]:
        """検索結果をキャッシュから取得"""
        data = await self.redis.get(f"search:{cache_key}")
        return json.loads(data) if data else None

    async def set_search_results(
        self,
        cache_key: str,
        results: list,
        ttl: int = 3600
    ):
        """検索結果をキャッシュに保存（デフォルト1時間）"""
        await self.redis.setex(
            f"search:{cache_key}",
            ttl,
            json.dumps(results, ensure_ascii=False)
        )
```

#### 3.3.2 キャッシュキー戦略

- 法令詳細: `law:{law_id}`
- 検索結果: `search:{hash(query_params)}`
- TTL: 法令詳細24時間、検索結果1時間

### 3.4 エラーハンドリング

```python
# app/core/exceptions.py

class EGovAPIError(Exception):
    """e-gov API エラー基底クラス"""
    pass

class LawNotFoundError(EGovAPIError):
    """法令が見つからない"""
    pass

class EGovAPITimeoutError(EGovAPIError):
    """e-gov API タイムアウト"""
    pass

class EGovAPIRateLimitError(EGovAPIError):
    """e-gov API レート制限"""
    pass
```

## 4. テスト仕様

### 4.1 単体テスト

```python
# tests/test_egov_client.py

import pytest
from app.services.egov_client import EGovAPIClient

@pytest.mark.asyncio
async def test_search_laws():
    """法令検索テスト"""
    client = EGovAPIClient(base_url="https://elaws.e-gov.go.jp")
    results = await client.search_laws("会社法")
    assert len(results) > 0
    assert results[0].law_name == "会社法"

@pytest.mark.asyncio
async def test_get_law_detail():
    """法令詳細取得テスト"""
    client = EGovAPIClient(base_url="https://elaws.e-gov.go.jp")
    law = await client.get_law_detail("405AC0000000087")
    assert law.law_name == "会社法"
    assert law.full_text is not None
```

### 4.2 統合テスト

```python
# tests/integration/test_law_api.py

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_search_laws_api():
    """法令検索APIテスト"""
    response = client.get("/api/v1/laws/search?q=会社法")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0
    assert len(data["results"]) > 0
```

## 5. パフォーマンス要件

- 検索API: 平均500ms以内（キャッシュミス時）
- 検索API: 平均100ms以内（キャッシュヒット時）
- 詳細取得API: 平均300ms以内（キャッシュミス時）
- 詳細取得API: 平均50ms以内（キャッシュヒット時）

## 6. セキュリティ考慮事項

- e-gov APIへのリクエストにUser-Agent設定
- レート制限の実装（60req/min/IP）
- 入力バリデーション（SQLインジェクション対策）
- XSS対策（レスポンスのサニタイズ）

## 7. 実装手順

1. **ステップ1**: データモデル定義（`app/models/law.py`）
2. **ステップ2**: e-gov APIクライアント実装（`app/services/egov_client.py`）
3. **ステップ3**: キャッシュ層実装（`app/core/cache.py`）
4. **ステップ4**: APIエンドポイント実装（`app/api/endpoints/laws.py`）
5. **ステップ5**: 単体テスト作成
6. **ステップ6**: 統合テスト作成
7. **ステップ7**: ドキュメント生成（Swagger）

## 8. 依存関係

- httpx (非同期HTTPクライアント)
- redis (キャッシュ)
- pydantic (データバリデーション)
- FastAPI (APIフレームワーク)

## 9. 完了条件

- [ ] すべてのエンドポイントが実装され動作する
- [ ] 単体テストカバレッジ80%以上
- [ ] 統合テストが全てパス
- [ ] パフォーマンス要件を満たす
- [ ] Swagger UIで仕様が確認できる
- [ ] コードレビュー完了

## 10. 備考

- e-gov APIの利用規約を確認し遵守すること
- APIの変更を監視し、アダプターパターンで対応可能にすること
- ログは適切なレベルで記録すること（INFO, WARNING, ERROR）
