"""
法令データモデル

このモジュールは法令検索結果、法令詳細、改正情報を表すPydanticモデルを定義します。
"""

from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List, Dict, Any


class LawSearchResult(BaseModel):
    """法令検索結果

    e-gov法令APIから取得した検索結果を表すモデル。

    Attributes:
        law_id: 法令ID（e-gov内部ID）
        law_number: 法令番号（例: 平成十七年法律第八十七号）
        law_name: 法令名
        law_type: 法令種別（法律、政令、省令など）
        promulgation_date: 公布日
        enforcement_date: 施行日（未施行の場合はNone）
    """
    law_id: str = Field(..., description="法令ID")
    law_number: str = Field(..., description="法令番号（例: 平成十七年法律第八十七号）")
    law_name: str = Field(..., description="法令名")
    law_type: str = Field(..., description="法令種別（法律、政令、省令など）")
    promulgation_date: date = Field(..., description="公布日")
    enforcement_date: Optional[date] = Field(None, description="施行日")

    class Config:
        json_schema_extra = {
            "example": {
                "law_id": "405AC0000000087",
                "law_number": "平成十七年法律第八十七号",
                "law_name": "会社法",
                "law_type": "法律",
                "promulgation_date": "2005-07-26",
                "enforcement_date": "2006-05-01"
            }
        }


class LawDetail(BaseModel):
    """法令詳細

    特定の法令の全文および詳細情報を表すモデル。

    Attributes:
        law_id: 法令ID
        law_number: 法令番号
        law_name: 法令名
        law_type: 法令種別
        promulgation_date: 公布日
        enforcement_date: 施行日
        full_text: 全文テキスト
        toc: 目次構造（章、条文の階層情報）
        metadata: その他のメタデータ
    """
    law_id: str = Field(..., description="法令ID")
    law_number: str = Field(..., description="法令番号")
    law_name: str = Field(..., description="法令名")
    law_type: str = Field(..., description="法令種別")
    promulgation_date: date = Field(..., description="公布日")
    enforcement_date: Optional[date] = Field(None, description="施行日")
    full_text: str = Field(..., description="法令全文")
    toc: List[Dict[str, Any]] = Field(default_factory=list, description="目次構造")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="メタデータ")

    class Config:
        json_schema_extra = {
            "example": {
                "law_id": "405AC0000000087",
                "law_number": "平成十七年法律第八十七号",
                "law_name": "会社法",
                "law_type": "法律",
                "promulgation_date": "2005-07-26",
                "enforcement_date": "2006-05-01",
                "full_text": "（全文テキスト）",
                "toc": [
                    {
                        "chapter": "第一章",
                        "title": "総則",
                        "articles": ["1", "2", "3"]
                    }
                ],
                "metadata": {
                    "last_updated": "2024-06-15"
                }
            }
        }


class LawAmendment(BaseModel):
    """法令改正情報

    特定の法令の改正履歴を表すモデル。

    Attributes:
        amendment_id: 改正ID
        law_id: 対象法令ID
        amendment_law_number: 改正法令番号
        amendment_date: 改正日
        enforcement_date: 改正施行日
        summary: 改正概要
    """
    amendment_id: str = Field(..., description="改正ID")
    law_id: str = Field(..., description="対象法令ID")
    amendment_law_number: str = Field(..., description="改正法令番号")
    amendment_date: date = Field(..., description="改正日")
    enforcement_date: Optional[date] = Field(None, description="改正施行日")
    summary: str = Field(..., description="改正概要")

    class Config:
        json_schema_extra = {
            "example": {
                "amendment_id": "令和元年法律第70号",
                "law_id": "405AC0000000087",
                "amendment_law_number": "令和元年法律第七十号",
                "amendment_date": "2019-12-11",
                "enforcement_date": "2021-03-01",
                "summary": "株主総会資料の電子提供制度の創設等"
            }
        }


class LawSearchResponse(BaseModel):
    """法令検索APIレスポンス

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
    results: List[LawSearchResult] = Field(..., description="検索結果")

    class Config:
        json_schema_extra = {
            "example": {
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
        }


class LawHistoryResponse(BaseModel):
    """法令改正履歴APIレスポンス

    特定法令の改正履歴一覧。

    Attributes:
        law_id: 法令ID
        law_name: 法令名
        amendments: 改正履歴リスト
    """
    law_id: str = Field(..., description="法令ID")
    law_name: str = Field(..., description="法令名")
    amendments: List[LawAmendment] = Field(..., description="改正履歴")

    class Config:
        json_schema_extra = {
            "example": {
                "law_id": "405AC0000000087",
                "law_name": "会社法",
                "amendments": [
                    {
                        "amendment_id": "令和元年法律第70号",
                        "law_id": "405AC0000000087",
                        "amendment_law_number": "令和元年法律第七十号",
                        "amendment_date": "2019-12-11",
                        "enforcement_date": "2021-03-01",
                        "summary": "株主総会資料の電子提供制度の創設等"
                    }
                ]
            }
        }
