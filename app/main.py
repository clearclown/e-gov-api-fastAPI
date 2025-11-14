"""
FastAPI メインアプリケーション
日本の法令・判例情報にアクセスするためのAPIサーバー
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import analytics, conversation, summarization

# FastAPIアプリケーションの作成
app = FastAPI(
    title="e-Gov Legal Information API",
    description="""
    日本の法令・判例情報にアクセスするためのAPI

    ## 主な機能

    ### Analytics（分析）
    - 法令・判例の関連性分析
    - 引用グラフの可視化
    - 最も引用されている法令のランキング

    ### Conversation（会話型相談）
    - 会話履歴を考慮した法律相談
    - 自然言語での質問に対応
    - 関連法令・判例の自動検索

    ### Summarization（要約）
    - 判例の自動要約（簡潔/詳細/平易）
    - 法令条文の平易な解説
    - 法令比較

    ## 開発状況
    - Phase 4: 高度な分析機能（実装完了）
    - Phase 3: AI統合（実装予定）
    - Phase 2: 判例API（実装予定）
    - Phase 1: 法令API（実装予定）

    ※ 現在はPhase 4の機能をモック実装で提供しています
    """,
    version="0.1.0",
    contact={
        "name": "e-Gov API Project",
    },
    license_info={
        "name": "MIT",
    },
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切に設定すること
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターの登録
app.include_router(analytics.router)
app.include_router(conversation.router)
app.include_router(summarization.router)


@app.get("/", tags=["root"])
async def root() -> dict:
    """
    ルートエンドポイント

    API情報を返却します
    """
    return {
        "name": "e-Gov Legal Information API",
        "version": "0.1.0",
        "status": "Phase 4 - Advanced Analytics (Mock Implementation)",
        "documentation": "/docs",
        "features": {
            "analytics": "法令・判例の関連性分析",
            "conversation": "会話型法律相談",
            "summarization": "法的文書の自動要約",
        },
    }


@app.get("/health", tags=["health"])
async def health_check() -> dict:
    """
    ヘルスチェックエンドポイント

    サーバーの稼働状態を確認します
    """
    return {
        "status": "healthy",
        "service": "e-gov-api-fastapi",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
