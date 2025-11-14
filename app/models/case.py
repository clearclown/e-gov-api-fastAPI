"""Case law data models"""

from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class CaseSummary(BaseModel):
    """判例の概要情報"""

    case_id: str = Field(..., description="判例ID")
    case_number: str = Field(..., description="事件番号")
    case_name: str = Field(..., description="事件名")
    court_name: str = Field(..., description="裁判所名")
    decision_date: date = Field(..., description="判決日")
    case_type: Optional[str] = Field(None, description="事件種別")

    class Config:
        json_schema_extra = {
            "example": {
                "case_id": "2023-12345",
                "case_number": "令和5年(オ)第1234号",
                "case_name": "損害賠償請求事件",
                "court_name": "最高裁判所第一小法廷",
                "decision_date": "2023-09-15",
                "case_type": "民事",
            }
        }


class CaseDetail(CaseSummary):
    """判例の詳細情報"""

    summary: str = Field(..., description="判例要旨")
    holdings: Optional[str] = Field(None, description="判示事項")
    case_summary: Optional[str] = Field(None, description="裁判要旨")
    main_text: str = Field(..., description="判決全文")
    cited_laws: Optional[list[str]] = Field(default_factory=list, description="引用法令")
    related_cases: Optional[list[str]] = Field(default_factory=list, description="関連判例")

    class Config:
        json_schema_extra = {
            "example": {
                "case_id": "2023-12345",
                "case_number": "令和5年(オ)第1234号",
                "case_name": "損害賠償請求事件",
                "court_name": "最高裁判所第一小法廷",
                "decision_date": "2023-09-15",
                "case_type": "民事",
                "summary": "契約違反による損害賠償請求において...",
                "holdings": "1. 契約上の義務違反の成立要件\n2. 損害賠償の範囲",
                "case_summary": "本件は、売買契約における債務不履行を理由とする損害賠償請求事件である...",
                "main_text": "主文\n1. 原判決を破棄する。\n2. ...",
                "cited_laws": ["民法第415条", "民法第709条"],
                "related_cases": ["平成20年(受)第1234号"],
            }
        }
