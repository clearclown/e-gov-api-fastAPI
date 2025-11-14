"""Law data models"""

from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class LawSummary(BaseModel):
    """法令の概要情報"""

    law_id: str = Field(..., description="法令ID")
    law_number: str = Field(..., description="法令番号")
    law_name: str = Field(..., description="法令名")
    promulgation_date: Optional[date] = Field(None, description="公布日")
    enforcement_date: Optional[date] = Field(None, description="施行日")
    category: Optional[str] = Field(None, description="法令カテゴリ")

    class Config:
        json_schema_extra = {
            "example": {
                "law_id": "321AC0000000086",
                "law_number": "平成十七年法律第八十六号",
                "law_name": "会社法",
                "promulgation_date": "2005-07-26",
                "enforcement_date": "2006-05-01",
                "category": "商法",
            }
        }


class LawDetail(LawSummary):
    """法令の詳細情報"""

    full_text: str = Field(..., description="法令全文")
    toc: Optional[str] = Field(None, description="目次")
    appendix: Optional[str] = Field(None, description="附則")
    last_updated: Optional[date] = Field(None, description="最終更新日")

    class Config:
        json_schema_extra = {
            "example": {
                "law_id": "321AC0000000086",
                "law_number": "平成十七年法律第八十六号",
                "law_name": "会社法",
                "promulgation_date": "2005-07-26",
                "enforcement_date": "2006-05-01",
                "category": "商法",
                "full_text": "第一条 この法律は、株式会社...",
                "toc": "第一編 総則\n第二編 株式会社...",
                "appendix": "附則（平成十七年七月二十六日法律第八十六号）",
                "last_updated": "2023-06-14",
            }
        }
