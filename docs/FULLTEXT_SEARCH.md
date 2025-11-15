# PostgreSQL 全文検索実装ガイド

## 概要

判例検索APIでは、PostgreSQLのGINインデックスを使用した高速な全文検索機能を実装しています。

## 実装内容

### 1. GINインデックス

マイグレーション `002_add_fulltext_search_index.py` でGINインデックスを作成：

```sql
CREATE INDEX idx_cases_fulltext ON cases USING gin(
    to_tsvector('simple',
        case_name || ' ' ||
        COALESCE(summary, '') || ' ' ||
        main_text
    )
)
```

このインデックスは以下のフィールドを対象とします：
- `case_name` - 事件名
- `summary` - 要旨
- `main_text` - 判決全文

### 2. 検索実装

`CaseRepository.search_cases()` メソッドで2つの検索モードをサポート：

#### a) PostgreSQL全文検索（use_fulltext=True、デフォルト）

```python
# to_tsvector でドキュメントをベクトル化
tsvector_expr = func.to_tsvector(
    'simple',
    func.concat(
        CaseModel.case_name,
        ' ',
        func.coalesce(CaseModel.summary, ''),
        ' ',
        CaseModel.main_text
    )
)

# plainto_tsquery でクエリを変換
tsquery_expr = func.plainto_tsquery('simple', query)

# @@ 演算子でマッチング
stmt = stmt.where(tsvector_expr.op('@@')(tsquery_expr))
```

**特徴：**
- GINインデックスを使用した高速検索
- 自然言語クエリ対応（`plainto_tsquery`）
- 大量のテキストデータでも高速

#### b) ILIKE検索（use_fulltext=False）

```python
search_filter = (
    CaseModel.case_name.ilike(f"%{query}%")
    | CaseModel.summary.ilike(f"%{query}%")
    | CaseModel.main_text.ilike(f"%{query}%")
)
stmt = stmt.where(search_filter)
```

**特徴：**
- GINインデックスがない環境でも動作
- 部分一致検索
- 大量データでは遅い

### 3. 使用例

```python
# デフォルト（全文検索）
results, total = await repo.search_cases(query="損害賠償")

# 明示的に全文検索を指定
results, total = await repo.search_cases(query="損害賠償", use_fulltext=True)

# ILIKE検索を使用
results, total = await repo.search_cases(query="損害賠償", use_fulltext=False)
```

## 日本語対応について

### 現在の実装

現在は `'simple'` text search configuration を使用しています。これは：
- 言語に依存しない基本的な検索
- すべての環境で動作
- 日本語でも基本的な検索が可能

### より高度な日本語検索

本番環境でより高度な日本語検索が必要な場合、以下の拡張を検討してください：

#### Option 1: pg_bigm

Bigramベースの全文検索：

```sql
-- 拡張のインストール
CREATE EXTENSION pg_bigm;

-- インデックス作成
CREATE INDEX idx_cases_bigm ON cases USING gin(
    (case_name || ' ' || COALESCE(summary, '') || ' ' || main_text) gin_bigm_ops
);
```

**特徴：**
- 日本語の部分一致検索に強い
- インストールが必要

#### Option 2: MeCab + textsearch_ja

形態素解析ベースの検索：

```sql
-- 拡張のインストール
CREATE EXTENSION textsearch_ja;

-- 日本語用のtext search configuration
CREATE TEXT SEARCH CONFIGURATION japanese (COPY = simple);

-- インデックス作成
CREATE INDEX idx_cases_japanese ON cases USING gin(
    to_tsvector('japanese', case_name || ' ' || COALESCE(summary, '') || ' ' || main_text)
);
```

**特徴：**
- 正確な日本語の単語区切り
- インストールと設定が複雑

## パフォーマンス

### ベンチマーク（想定）

| データ件数 | ILIKE検索 | 全文検索（GIN） |
|-----------|----------|----------------|
| 1,000件   | 50ms     | 5ms            |
| 10,000件  | 500ms    | 10ms           |
| 100,000件 | 5,000ms  | 20ms           |
| 1,000,000件| 50,000ms | 30ms          |

**注意：** 実際のパフォーマンスはデータの内容やクエリによって異なります。

### インデックスサイズ

GINインデックスはディスク容量を消費します：
- 概算: 元のテキストデータの30-50%程度
- 例: 判決全文が平均10KBの場合、100万件で約3-5GB

## トラブルシューティング

### GINインデックスが使用されない場合

1. **インデックスが作成されているか確認**
   ```sql
   \di idx_cases_fulltext
   ```

2. **ANALYZEを実行**
   ```sql
   ANALYZE cases;
   ```

3. **EXPLAINで実行計画を確認**
   ```sql
   EXPLAIN ANALYZE
   SELECT * FROM cases
   WHERE to_tsvector('simple', case_name || ' ' || COALESCE(summary, '') || ' ' || main_text)
         @@ plainto_tsquery('simple', '損害賠償');
   ```

### 検索結果が期待通りでない場合

1. **text search configurationを確認**
   - 'simple' は基本的な検索のみ
   - 日本語の高度な検索には pg_bigm や textsearch_ja が必要

2. **クエリの形式を確認**
   - `plainto_tsquery` は自然言語クエリ用
   - より制御が必要な場合は `to_tsquery` を使用

## マイグレーション

### GINインデックスの追加

```bash
# マイグレーション適用
alembic upgrade head
```

### ロールバック

```bash
# インデックス削除
alembic downgrade -1
```

## テスト

全文検索機能のテスト：

```bash
# 全文検索テストを実行
pytest tests/unit/test_case_repository.py::test_fulltext_search -v
```

## 参考資料

- [PostgreSQL Full Text Search](https://www.postgresql.org/docs/current/textsearch.html)
- [GIN Indexes](https://www.postgresql.org/docs/current/gin.html)
- [pg_bigm](https://pgbigm.osdn.jp/)
