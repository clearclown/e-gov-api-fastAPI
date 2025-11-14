"""法令データモデル"""

from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class LawDetail(BaseModel):
    """法令詳細データ"""

    law_id: str = Field(..., description="法令ID")
    law_name: str = Field(..., description="法令名")
    law_number: Optional[str] = Field(None, description="法令番号")
    promulgation_date: Optional[date] = Field(None, description="公布日")
    enforcement_date: Optional[date] = Field(None, description="施行日")
    category: Optional[str] = Field(None, description="分野")
    full_text: str = Field(..., description="法令全文")
    updated_at: Optional[date] = Field(None, description="最終更新日")

    class Config:
        json_schema_extra = {
            "example": {
                "law_id": "405AC0000000087",
                "law_name": "民法",
                "law_number": "明治二十九年法律第八十九号",
                "promulgation_date": "1896-04-27",
                "enforcement_date": "1898-07-16",
                "category": "民事",
                "full_text": "第一編 総則...",
                "updated_at": "2024-01-01",
            }
        }


class LawSearchResult(BaseModel):
    """法令検索結果"""

    law_id: str
    law_name: str
    law_number: Optional[str] = None
    category: Optional[str] = None
    relevance_score: Optional[float] = Field(None, ge=0.0, le=1.0)
