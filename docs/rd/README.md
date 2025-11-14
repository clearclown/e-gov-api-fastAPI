# 要件定義（RD）ドキュメント

このディレクトリには、e-gov API FastAPIプロジェクトの要件定義および機能仕様書が格納されています。

## ドキュメント一覧

### 1. [要件定義書](./requirements.md)
プロジェクト全体の要件定義書です。以下の内容を含みます：

- プロジェクト概要・背景
- 機能要件（FR-001 ～ FR-017）
- 非機能要件（NFR-001 ～ NFR-013）
- 技術要件
- 制約事項
- リスク管理
- スケジュール

**対象者**: プロジェクトマネージャー、技術リーダー、全開発メンバー

---

### 2. [機能仕様書: 法令API（Phase 1）](./feature-01-law-api.md)
**機能ID**: FEAT-001

e-gov法令APIとの連携、法令検索・取得機能の詳細仕様です。

**主な内容**:
- e-gov APIクライアント設計
- データモデル（LawSearchResult, LawDetail, LawAmendment）
- REST APIエンドポイント（検索、詳細取得、改正履歴）
- キャッシング戦略（Redis）
- エラーハンドリング

**対象者**: バックエンド開発者（Phase 1担当）

**関連要件**: FR-001, FR-002, FR-003, FR-007, FR-008, FR-009

---

### 3. [機能仕様書: 判例API（Phase 2）](./feature-02-case-api.md)
**機能ID**: FEAT-002
**依存**: FEAT-001

判例データの取得・検索機能の詳細仕様です。

**主な内容**:
- 判例データモデル（CaseSearchResult, CaseDetail）
- データベーススキーマ（PostgreSQL + 全文検索）
- 判例スクレイパー設計
- REST APIエンドポイント（判例検索、詳細取得）
- バッチ処理

**対象者**: バックエンド開発者（Phase 2担当）

**関連要件**: FR-004, FR-005, FR-006, FR-010, FR-011

---

### 4. [機能仕様書: AI統合（Phase 3）](./feature-03-ai-integration.md)
**機能ID**: FEAT-003
**依存**: FEAT-001, FEAT-002

Agentic RAGとClaude Agent SDKの統合仕様です。

**主な内容**:
- RAGアーキテクチャ設計
- ベクトルストア設計（pgvector）
- 埋め込み生成バッチ処理
- Claude Agent SDK統合
- MCPツール定義（search_law, search_case, ask_legal_question など）
- MCP設定ファイル

**対象者**: AI/ML担当開発者、バックエンド開発者（Phase 3担当）

**関連要件**: FR-012, FR-013, FR-014

---

### 5. [機能仕様書: 高度な分析機能（Phase 4）](./feature-04-advanced-features.md)
**機能ID**: FEAT-004
**依存**: FEAT-001, FEAT-002, FEAT-003

法令・判例の関連性分析、会話型相談、文書要約などの高度な機能仕様です。

**主な内容**:
- 引用グラフ構築（NetworkX）
- 関連性分析アルゴリズム
- 会話履歴管理
- 自然言語法律相談
- 判例要約機能
- 法令条文の平易な説明

**対象者**: AI/ML担当開発者、バックエンド開発者（Phase 4担当）

**関連要件**: FR-015, FR-016, FR-017

---

## ドキュメントの読み方

### 開発フェーズ別

#### Phase 1（基盤構築）を担当する場合
1. [要件定義書](./requirements.md) - 全体像を把握
2. [機能仕様書: 法令API](./feature-01-law-api.md) - 実装詳細を確認

#### Phase 2（判例データ統合）を担当する場合
1. [要件定義書](./requirements.md) - 全体像を把握
2. [機能仕様書: 法令API](./feature-01-law-api.md) - 依存する機能を確認
3. [機能仕様書: 判例API](./feature-02-case-api.md) - 実装詳細を確認

#### Phase 3（AI統合）を担当する場合
1. [要件定義書](./requirements.md) - 全体像を把握
2. [機能仕様書: 法令API](./feature-01-law-api.md) - 既存APIを理解
3. [機能仕様書: 判例API](./feature-02-case-api.md) - 既存APIを理解
4. [機能仕様書: AI統合](./feature-03-ai-integration.md) - 実装詳細を確認

#### Phase 4（高度な機能）を担当する場合
全てのドキュメントを順番に読むことを推奨

### 役割別

#### プロジェクトマネージャー
- [要件定義書](./requirements.md) - 特にスケジュール、リスク管理セクション

#### 技術リーダー
- 全てのドキュメントの「アーキテクチャ」「技術選定」セクション

#### バックエンド開発者
- 担当フェーズの機能仕様書の「実装手順」「テスト仕様」セクション

#### AI/ML担当者
- [機能仕様書: AI統合](./feature-03-ai-integration.md)
- [機能仕様書: 高度な分析機能](./feature-04-advanced-features.md)

---

## 機能間の依存関係

```
FEAT-001 (法令API)
    ↓
FEAT-002 (判例API)
    ↓
FEAT-003 (AI統合)
    ↓
FEAT-004 (高度な分析)
```

各機能は前フェーズの完了が必要です。

---

## 要件トレーサビリティ

### 機能要件（FR）と機能仕様（FEAT）のマッピング

| 要件ID | 要件名 | 実装機能 |
|--------|--------|----------|
| FR-001 | e-gov法令APIとの連携 | FEAT-001 |
| FR-002 | 法令改正履歴管理 | FEAT-001 |
| FR-003 | 法令データキャッシング | FEAT-001 |
| FR-004 | 判例データ取得 | FEAT-002 |
| FR-005 | 判例データ構造化 | FEAT-002 |
| FR-006 | 判例データベース構築 | FEAT-002 |
| FR-007 | 法令検索API | FEAT-001 |
| FR-008 | 法令詳細取得API | FEAT-001 |
| FR-009 | 法令改正履歴API | FEAT-001 |
| FR-010 | 判例検索API | FEAT-002 |
| FR-011 | 判例詳細取得API | FEAT-002 |
| FR-012 | Agentic RAG実装 | FEAT-003 |
| FR-013 | Claude Agent SDK統合 | FEAT-003 |
| FR-014 | MCP Tool定義 | FEAT-003 |
| FR-015 | 法令・判例関連性分析 | FEAT-004 |
| FR-016 | 自然言語法律相談 | FEAT-004 |
| FR-017 | 法的文書自動要約 | FEAT-004 |

---

## ドキュメント更新ルール

### 更新が必要な場合

1. **要件の変更・追加**
   - [要件定義書](./requirements.md)を更新
   - 影響を受ける機能仕様書も更新

2. **技術選定の変更**
   - 該当する機能仕様書の「依存関係」セクションを更新

3. **APIエンドポイントの変更**
   - 該当する機能仕様書のAPI仕様セクションを更新
   - OpenAPI仕様書（Swagger）も連動更新

4. **実装完了時**
   - 機能仕様書の「ステータス」を更新
   - 「完了条件」のチェックリストを更新

### 更新手順

1. 該当ドキュメントを編集
2. 「改訂履歴」テーブルに記録（要件定義書の場合）
3. 関連ドキュメントの整合性を確認
4. プルリクエストでレビュー依頼

---

## 質問・フィードバック

ドキュメントに関する質問や改善提案は、以下の方法で受け付けます：

- GitHub Issues（推奨）
- プロジェクトチャット
- 技術リーダーへ直接連絡

---

## 参考資料

### 外部仕様
- [e-gov法令API仕様](https://elaws.e-gov.go.jp/)
- [裁判所ウェブサイト](https://www.courts.go.jp/)
- [Claude Agent SDK Documentation](https://code.claude.com/docs/ja/sdk/migration-guide)

### 技術ドキュメント
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [pgvector Documentation](https://github.com/pgvector/pgvector)

---

**最終更新**: 2025-11-14
**管理者**: プロジェクト技術リーダー
