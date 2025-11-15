# 開発者向けドキュメント

## 実装完了状況

### Phase 1: 基盤構築 ✅

以下の機能が実装完了しました：

#### 1. プロジェクト構造
```
e-gov-api-fastAPI/
├── app/
│   ├── api/
│   │   └── endpoints/
│   │       └── laws.py          # 法令APIエンドポイント
│   ├── core/
│   │   ├── cache.py             # Redisキャッシュ層
│   │   ├── config.py            # 設定管理
│   │   └── exceptions.py        # カスタム例外
│   ├── models/
│   │   └── law.py               # データモデル
│   ├── services/
│   │   └── egov_client.py       # e-gov APIクライアント
│   └── main.py                  # メインアプリケーション
├── tests/
│   ├── unit/
│   │   └── test_egov_client.py  # 単体テスト
│   ├── integration/
│   │   └── test_law_api.py      # 統合テスト
│   └── conftest.py              # pytest設定
├── pyproject.toml               # パッケージ設定
├── .env.example                 # 環境変数サンプル
└── README_DEV.md                # このファイル
```

#### 2. 実装済み機能

##### データモデル (`app/models/law.py`)
- ✅ `LawSearchResult` - 法令検索結果
- ✅ `LawDetail` - 法令詳細
- ✅ `LawAmendment` - 改正情報
- ✅ `LawSearchResponse` - 検索APIレスポンス
- ✅ `LawHistoryResponse` - 改正履歴APIレスポンス

##### コア機能 (`app/core/`)
- ✅ 設定管理 (環境変数からの読み込み)
- ✅ カスタム例外クラス
- ✅ Redisキャッシュ機能
- ✅ エラーハンドリング

##### e-gov APIクライアント (`app/services/egov_client.py`)
- ✅ 法令検索機能
- ✅ 法令詳細取得
- ✅ 改正履歴取得
- ✅ タイムアウト処理
- ✅ レート制限対応
- ✅ XML解析

##### REST APIエンドポイント
- ✅ `GET /api/v1/laws/search` - 法令検索
- ✅ `GET /api/v1/laws/{law_id}` - 法令詳細取得
- ✅ `GET /api/v1/laws/{law_id}/history` - 改正履歴取得
- ✅ `GET /` - ルートエンドポイント
- ✅ `GET /health` - ヘルスチェック

##### テスト
- ✅ 単体テスト (e-gov APIクライアント)
- ✅ 統合テスト (APIエンドポイント)
- ✅ モック使用のテストケース

## セットアップ手順

### 1. 依存関係のインストール

```bash
# uvを使用（推奨）
uv venv
source .venv/bin/activate  # Linux/Mac
uv pip install -e ".[dev]"

# または通常のpip
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 2. 環境変数の設定

```bash
cp .env.example .env
# 必要に応じて.envを編集
```

### 3. アプリケーションの起動

```bash
# 開発サーバー起動
python -m app.main

# または uvicorn で直接起動
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. API動作確認

ブラウザで以下にアクセス：
- API ドキュメント: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- ヘルスチェック: http://localhost:8000/health

### 5. テストの実行

```bash
# 全テスト実行
pytest

# カバレッジ付き
pytest --cov=app --cov-report=html

# 特定のテストのみ
pytest tests/unit/test_egov_client.py
pytest tests/integration/test_law_api.py
```

## API使用例

### 1. 法令検索

```bash
curl "http://localhost:8000/api/v1/laws/search?q=会社法&limit=10"
```

レスポンス:
```json
{
  "total": 1,
  "limit": 10,
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

### 2. 法令詳細取得

```bash
curl "http://localhost:8000/api/v1/laws/405AC0000000087"
```

### 3. 改正履歴取得

```bash
curl "http://localhost:8000/api/v1/laws/405AC0000000087/history"
```

## 重要な注意事項

### e-gov API統合について

現在の実装は、e-gov APIの仕様に基づいた**モック実装**です。実際のe-gov APIと連携する際は、以下の調整が必要です：

1. **APIエンドポイントの確認**
   - 実際のe-gov APIのエンドポイントURLを確認
   - `app/services/egov_client.py` の `SEARCH_ENDPOINT` と `DETAIL_ENDPOINT` を修正

2. **XMLレスポンス構造の調整**
   - 実際のXMLレスポンス構造を確認
   - `_parse_search_response()` と `_parse_detail_response()` メソッドを修正

3. **認証の追加**
   - APIキーが必要な場合は、認証ヘッダーを追加
   - `app/core/config.py` に認証情報の設定を追加

4. **改正履歴APIの実装**
   - e-gov APIの改正履歴エンドポイントを確認
   - `get_law_history()` メソッドを実装

### キャッシュについて

- デフォルトでRedisキャッシュが有効
- Redisが利用できない場合は自動的に無効化
- 環境変数 `REDIS_ENABLED=false` でキャッシュを無効化可能

### パフォーマンス要件

仕様書で定義されたパフォーマンス要件：
- 検索API: 平均500ms以内（キャッシュミス時）
- 検索API: 平均100ms以内（キャッシュヒット時）
- 詳細取得API: 平均300ms以内（キャッシュミス時）
- 詳細取得API: 平均50ms以内（キャッシュヒット時）

実際のe-gov API統合後にパフォーマンステストを実施してください。

## 今後の開発予定

### Phase 2: 判例データ統合
- [ ] 判例データソースの選定
- [ ] スクレイピング/APIクライアント実装
- [ ] 判例検索エンドポイント

### Phase 3: AI統合
- [ ] Agentic RAG実装
- [ ] Claude Agent SDK統合
- [ ] MCPサーバー機能

### Phase 4: 高度な機能
- [ ] 法令・判例の関連性分析
- [ ] 自然言語法律相談
- [ ] 法的文書自動要約

## トラブルシューティング

### Q: テストが失敗する

A: Redisが起動しているか確認してください。テスト時はキャッシュが自動的に無効化されますが、一部の統合テストで問題が発生する可能性があります。

### Q: e-gov APIへの接続が失敗する

A: 現在の実装はモックです。実際のe-gov APIのエンドポイントとXML構造に合わせて調整が必要です。

### Q: パフォーマンスが遅い

A:
1. Redisキャッシュが有効か確認
2. e-gov APIのタイムアウト設定を確認
3. ネットワーク接続を確認

## 貢献方法

1. ブランチを作成
2. 変更を実装
3. テストを追加/更新
4. プルリクエストを作成

## ライセンス

TBD
