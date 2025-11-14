# 機能仕様書: 判例API（Phase 2）

**機能ID**: FEAT-002
**担当者**: ［担当者名］
**作成日**: 2025-11-14
**ステータス**: 未着手
**依存**: FEAT-001（法令API）

## 1. 機能概要

裁判所ウェブサイトおよび判例データベースから判例情報を取得し、検索・提供する機能を実装する。

## 2. 対象要件

- FR-004: 判例データ取得
- FR-005: 判例データ構造化
- FR-006: 判例データベース構築
- FR-010: 判例検索API
- FR-011: 判例詳細取得API

## 3. 詳細仕様

### 3.1 データソース

#### 3.1.1 裁判所ウェブサイト
- URL: https://www.courts.go.jp/
- 最高裁判所判例集
- 下級裁判所判例集

#### 3.1.2 取得方法の選択肢
1. **公式API**（利用可能な場合優先）
2. **Webスクレイピング**（robots.txt遵守）
3. **オープンデータ**（利用可能な場合）

### 3.2 判例データモデル

```python
# app/models/case.py

from pydantic import BaseModel
from datetime import date
from typing import Optional, List
from enum import Enum

class CourtType(str, Enum):
    """裁判所種別"""
    SUPREME = "最高裁判所"
    HIGH = "高等裁判所"
    DISTRICT = "地方裁判所"
    FAMILY = "家庭裁判所"
    SUMMARY = "簡易裁判所"

class CaseType(str, Enum):
    """事件種別"""
    CIVIL = "民事"
    CRIMINAL = "刑事"
    ADMINISTRATIVE = "行政"
    FAMILY = "家事"

class CaseSearchResult(BaseModel):
    """判例検索結果"""
    case_id: str
    case_number: str  # 事件番号（例: 令和2年(オ)第123号）
    case_name: str    # 事件名
    court_type: CourtType
    court_name: str   # 裁判所名（例: 東京高等裁判所）
    case_type: CaseType
    decision_date: date  # 判決日
    summary: Optional[str]  # 要旨

class CaseDetail(BaseModel):
    """判例詳細"""
    case_id: str
    case_number: str
    case_name: str
    court_type: CourtType
    court_name: str
    case_type: CaseType
    decision_date: date
    summary: Optional[str]
    main_text: str  # 判決全文
    holdings: Optional[str]  # 判示事項
    case_summary: Optional[str]  # 裁判要旨
    references: List[str]  # 参照法令
    related_cases: List[str]  # 関連判例
    metadata: dict

class CaseReference(BaseModel):
    """判例引用情報"""
    case_id: str
    referenced_law_id: Optional[str]  # 引用法令ID
    referenced_case_id: Optional[str]  # 引用判例ID
    reference_type: str  # 引用種別
```

### 3.3 データベーススキーマ

```sql
-- PostgreSQL スキーマ

-- 判例テーブル
CREATE TABLE cases (
    case_id VARCHAR(50) PRIMARY KEY,
    case_number VARCHAR(100) NOT NULL,
    case_name VARCHAR(500) NOT NULL,
    court_type VARCHAR(50) NOT NULL,
    court_name VARCHAR(100) NOT NULL,
    case_type VARCHAR(50) NOT NULL,
    decision_date DATE NOT NULL,
    summary TEXT,
    main_text TEXT NOT NULL,
    holdings TEXT,
    case_summary TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_court_type CHECK (
        court_type IN ('最高裁判所', '高等裁判所', '地方裁判所', '家庭裁判所', '簡易裁判所')
    ),
    CONSTRAINT check_case_type CHECK (
        case_type IN ('民事', '刑事', '行政', '家事')
    )
);

-- 判例引用テーブル
CREATE TABLE case_references (
    id SERIAL PRIMARY KEY,
    case_id VARCHAR(50) NOT NULL REFERENCES cases(case_id),
    referenced_law_id VARCHAR(50),
    referenced_case_id VARCHAR(50),
    reference_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_referenced_case FOREIGN KEY (referenced_case_id)
        REFERENCES cases(case_id) ON DELETE CASCADE
);

-- 全文検索インデックス
CREATE INDEX idx_cases_fulltext ON cases USING gin(
    to_tsvector('japanese', case_name || ' ' || COALESCE(summary, '') || ' ' || main_text)
);

-- 検索用インデックス
CREATE INDEX idx_cases_decision_date ON cases(decision_date DESC);
CREATE INDEX idx_cases_court_type ON cases(court_type);
CREATE INDEX idx_cases_case_type ON cases(case_type);
CREATE INDEX idx_case_references_case_id ON case_references(case_id);
```

### 3.4 判例取得サービス

```python
# app/services/case_scraper.py

from typing import List, Optional
from datetime import date
import httpx
from bs4 import BeautifulSoup
from app.models.case import CaseSearchResult, CaseDetail

class CaseScraperService:
    """判例データ取得サービス"""

    def __init__(self, base_url: str = "https://www.courts.go.jp"):
        self.base_url = base_url
        self.session = httpx.AsyncClient(timeout=30)

    async def search_cases(
        self,
        query: Optional[str] = None,
        court_type: Optional[str] = None,
        case_type: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        limit: int = 50
    ) -> List[CaseSearchResult]:
        """判例検索"""
        # 実装詳細

    async def fetch_case_detail(self, case_id: str) -> CaseDetail:
        """判例詳細取得"""
        # 実装詳細

    async def parse_case_html(self, html: str) -> CaseDetail:
        """HTMLから判例データを抽出"""
        soup = BeautifulSoup(html, 'html.parser')
        # パース処理

    async def close(self):
        """セッションクローズ"""
        await self.session.aclose()
```

### 3.5 判例データリポジトリ

```python
# app/repositories/case_repository.py

from typing import List, Optional
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.case import CaseDetail, CaseSearchResult

class CaseRepository:
    """判例データベースアクセス"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_case(self, case: CaseDetail) -> str:
        """判例を保存"""
        # 実装詳細

    async def get_case_by_id(self, case_id: str) -> Optional[CaseDetail]:
        """判例ID で取得"""
        # 実装詳細

    async def search_cases(
        self,
        query: Optional[str] = None,
        court_type: Optional[str] = None,
        case_type: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[List[CaseSearchResult], int]:
        """判例検索（全文検索対応）"""
        # 実装詳細

    async def get_cases_by_law(self, law_id: str) -> List[CaseSearchResult]:
        """特定の法令を引用している判例を取得"""
        # 実装詳細
```

### 3.6 REST API エンドポイント

#### 3.6.1 判例検索API

**エンドポイント**: `GET /api/v1/cases/search`

**リクエストパラメータ**:
```
q: str (optional) - 検索キーワード（全文検索）
court: str (optional) - 裁判所種別
type: str (optional) - 事件種別（civil, criminal, administrative, family）
date_from: date (optional) - 判決日開始（YYYY-MM-DD）
date_to: date (optional) - 判決日終了（YYYY-MM-DD）
limit: int (optional, default=50, max=100) - 取得件数
offset: int (optional, default=0) - オフセット
```

**レスポンス例**:
```json
{
  "total": 87,
  "limit": 50,
  "offset": 0,
  "results": [
    {
      "case_id": "20200123456",
      "case_number": "令和2年(オ)第123号",
      "case_name": "損害賠償請求事件",
      "court_type": "最高裁判所",
      "court_name": "最高裁判所第一小法廷",
      "case_type": "民事",
      "decision_date": "2020-06-15",
      "summary": "労働契約における解雇の有効性が争われた事案"
    }
  ]
}
```

**実装**:
```python
# app/api/endpoints/cases.py

from fastapi import APIRouter, Query, Depends
from typing import Optional
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/v1/cases", tags=["cases"])

@router.get("/search")
async def search_cases(
    q: Optional[str] = Query(None, description="検索キーワード"),
    court: Optional[str] = Query(None, description="裁判所種別"),
    type: Optional[str] = Query(None, description="事件種別"),
    date_from: Optional[date] = Query(None, description="判決日開始"),
    date_to: Optional[date] = Query(None, description="判決日終了"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db_session)
):
    """判例検索API"""
    # 実装詳細
```

#### 3.6.2 判例詳細取得API

**エンドポイント**: `GET /api/v1/cases/{case_id}`

**パスパラメータ**:
```
case_id: str - 判例ID
```

**レスポンス例**:
```json
{
  "case_id": "20200123456",
  "case_number": "令和2年(オ)第123号",
  "case_name": "損害賠償請求事件",
  "court_type": "最高裁判所",
  "court_name": "最高裁判所第一小法廷",
  "case_type": "民事",
  "decision_date": "2020-06-15",
  "summary": "労働契約における解雇の有効性が争われた事案",
  "main_text": "（判決全文）",
  "holdings": "（判示事項）",
  "case_summary": "（裁判要旨）",
  "references": ["405AC0000000087"],
  "related_cases": ["20190234567"],
  "metadata": {
    "source": "courts.go.jp",
    "last_updated": "2024-11-14"
  }
}
```

#### 3.6.3 法令別判例取得API

**エンドポイント**: `GET /api/v1/laws/{law_id}/cases`

**パスパラメータ**:
```
law_id: str - 法令ID
```

**クエリパラメータ**:
```
limit: int (optional, default=50)
offset: int (optional, default=0)
```

**レスポンス例**:
```json
{
  "law_id": "405AC0000000087",
  "law_name": "会社法",
  "total": 234,
  "limit": 50,
  "offset": 0,
  "cases": [
    {
      "case_id": "20200123456",
      "case_number": "令和2年(オ)第123号",
      "case_name": "株主総会決議取消請求事件",
      "court_type": "最高裁判所",
      "decision_date": "2020-06-15",
      "summary": "株主総会決議の瑕疵が争われた事案"
    }
  ]
}
```

### 3.7 データ取得バッチ処理

```python
# app/batch/fetch_cases.py

import asyncio
from datetime import date, timedelta
from app.services.case_scraper import CaseScraperService
from app.repositories.case_repository import CaseRepository

async def fetch_recent_cases(days: int = 7):
    """最近の判例を取得して保存"""
    scraper = CaseScraperService()
    date_from = date.today() - timedelta(days=days)

    try:
        cases = await scraper.search_cases(
            date_from=date_from,
            limit=1000
        )

        async with get_db_session() as session:
            repo = CaseRepository(session)
            for case in cases:
                detail = await scraper.fetch_case_detail(case.case_id)
                await repo.save_case(detail)
            await session.commit()

        print(f"取得した判例数: {len(cases)}")

    finally:
        await scraper.close()

if __name__ == "__main__":
    asyncio.run(fetch_recent_cases(days=30))
```

## 4. テスト仕様

### 4.1 単体テスト

```python
# tests/test_case_scraper.py

import pytest
from app.services.case_scraper import CaseScraperService

@pytest.mark.asyncio
async def test_search_cases():
    """判例検索テスト"""
    scraper = CaseScraperService()
    results = await scraper.search_cases(query="損害賠償")
    assert len(results) > 0
    await scraper.close()

@pytest.mark.asyncio
async def test_fetch_case_detail():
    """判例詳細取得テスト"""
    scraper = CaseScraperService()
    case = await scraper.fetch_case_detail("20200123456")
    assert case.case_name is not None
    assert case.main_text is not None
    await scraper.close()
```

### 4.2 統合テスト

```python
# tests/integration/test_case_api.py

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_search_cases_api():
    """判例検索APIテスト"""
    response = client.get("/api/v1/cases/search?q=損害賠償")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 0
```

## 5. パフォーマンス要件

- 検索API: 平均600ms以内（データベース検索）
- 詳細取得API: 平均200ms以内（データベースから取得）
- バッチ処理: 100件/分以上の取得速度

## 6. セキュリティ考慮事項

- robots.txt の遵守
- User-Agent の適切な設定
- レート制限（スクレイピング時: 10req/min）
- 入力バリデーション

## 7. 実装手順

1. **ステップ1**: データモデル定義（`app/models/case.py`）
2. **ステップ2**: データベーススキーマ作成（マイグレーション）
3. **ステップ3**: リポジトリ層実装（`app/repositories/case_repository.py`）
4. **ステップ4**: スクレイパー実装（`app/services/case_scraper.py`）
5. **ステップ5**: APIエンドポイント実装（`app/api/endpoints/cases.py`）
6. **ステップ6**: バッチ処理実装（`app/batch/fetch_cases.py`）
7. **ステップ7**: テスト作成
8. **ステップ8**: ドキュメント更新

## 8. 依存関係

- SQLAlchemy (ORM)
- asyncpg (PostgreSQL driver)
- BeautifulSoup4 (HTMLパース)
- httpx (非同期HTTPクライアント)

## 9. 完了条件

- [ ] データベーススキーマが作成され、マイグレーション可能
- [ ] 判例データの取得・保存が動作する
- [ ] 全文検索が動作する
- [ ] 全APIエンドポイントが実装され動作する
- [ ] 単体テストカバレッジ80%以上
- [ ] 統合テストが全てパス
- [ ] バッチ処理が正常に動作する
- [ ] Swagger UIで仕様が確認できる

## 10. 備考

- 裁判所ウェブサイトのrobots.txtを確認すること
- スクレイピング頻度は控えめに設定すること
- 判例の著作権について確認すること
- データソースの変更に対応できるよう抽象化すること
