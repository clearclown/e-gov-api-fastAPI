"""
判例データモデル

このモジュールは裁判所判例の検索結果、詳細情報を表すPydanticモデルを定義します。
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import date
from typing import Optional, List, Dict, Any


class CaseSearchResult(BaseModel):
    """判例検索結果

    裁判所判例データベースから取得した検索結果を表すモデル。

    Attributes:
        case_id: 判例ID（内部ID）
        case_number: 事件番号（例: 令和2年(行ケ)第10001号）
        court_name: 裁判所名
        case_date: 判決日
        case_name: 事件名
        case_type: 事件種別（民事、刑事、行政など）
        summary: 判決要旨
    """
    case_id: str = Field(..., description="判例ID")
    case_number: str = Field(..., description="事件番号（例: 令和2年(行ケ)第10001号）")
    court_name: str = Field(..., description="裁判所名")
    case_date: date = Field(..., description="判決日")
    case_name: str = Field(..., description="事件名")
    case_type: str = Field(..., description="事件種別（民事、刑事、行政など）")
    summary: str = Field(default="", description="判決要旨")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "case_id": "2020WLJPCA01010001",
                "case_number": "令和2年(行ケ)第10001号",
                "court_name": "知的財産高等裁判所",
                "case_date": "2021-03-15",
                "case_name": "特許権侵害差止請求事件",
                "case_type": "行政",
                "summary": "特許権の侵害が認められ、差止請求を認容した事例"
            }
        }
    )


class CaseDetail(BaseModel):
    """判例詳細

    特定の判例の全文および詳細情報を表すモデル。

    Attributes:
        case_id: 判例ID
        case_number: 事件番号
        court_name: 裁判所名
        case_date: 判決日
        case_name: 事件名
        case_type: 事件種別
        summary: 判決要旨
        full_text: 判決全文
        related_laws: 関連法令リスト
        keywords: キーワードリスト
        references: 引用判例リスト
        metadata: その他のメタデータ
    """
    case_id: str = Field(..., description="判例ID")
    case_number: str = Field(..., description="事件番号")
    court_name: str = Field(..., description="裁判所名")
    case_date: date = Field(..., description="判決日")
    case_name: str = Field(..., description="事件名")
    case_type: str = Field(..., description="事件種別")
    summary: str = Field(default="", description="判決要旨")
    full_text: str = Field(..., description="判決全文")
    related_laws: List[str] = Field(default_factory=list, description="関連法令")
    keywords: List[str] = Field(default_factory=list, description="キーワード")
    references: List[str] = Field(default_factory=list, description="引用判例")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="メタデータ")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "case_id": "2020WLJPCA01010001",
                "case_number": "令和2年(行ケ)第10001号",
                "court_name": "知的財産高等裁判所",
                "case_date": "2021-03-15",
                "case_name": "特許権侵害差止請求事件",
                "case_type": "行政",
                "summary": "特許権の侵害が認められ、差止請求を認容した事例",
                "full_text": "判決全文テキスト...",
                "related_laws": ["特許法第100条", "民法第709条"],
                "keywords": ["特許権侵害", "差止請求", "損害賠償"],
                "references": ["平成30年(行ケ)第10123号"],
                "metadata": {
                    "source": "courts.go.jp",
                    "last_updated": "2024-06-15"
                }
            }
        }
    )


class CaseSearchResponse(BaseModel):
    """判例検索APIレスポンス

    検索結果のページネーション情報を含むレスポンス。

    Attributes:
        total: 総検索結果数
        limit: 1ページあたりの件数
        offset: オフセット
        results: 検索結果リスト
    """
    total: int = Field(..., description="総検索結果数")
    limit: int = Field(..., description="1ページあたりの件数")
    offset: int = Field(..., description="オフセット")
    results: List[CaseSearchResult] = Field(..., description="検索結果")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total": 50,
                "limit": 10,
                "offset": 0,
                "results": [
                    {
                        "case_id": "2020WLJPCA01010001",
                        "case_number": "令和2年(行ケ)第10001号",
                        "court_name": "知的財産高等裁判所",
                        "case_date": "2021-03-15",
                        "case_name": "特許権侵害差止請求事件",
                        "case_type": "行政",
                        "summary": "特許権の侵害が認められ、差止請求を認容した事例"
                    }
                ]
            }
        }
    )


class CourtInfo(BaseModel):
    """裁判所情報

    利用可能な裁判所の一覧情報。

    Attributes:
        court_id: 裁判所ID
        court_name: 裁判所名
        court_type: 裁判所種別（最高裁、高裁、地裁など）
        location: 所在地
    """
    court_id: str = Field(..., description="裁判所ID")
    court_name: str = Field(..., description="裁判所名")
    court_type: str = Field(..., description="裁判所種別")
    location: Optional[str] = Field(None, description="所在地")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "court_id": "IPHC",
                "court_name": "知的財産高等裁判所",
                "court_type": "高等裁判所",
                "location": "東京都千代田区"
            }
        }
    )
