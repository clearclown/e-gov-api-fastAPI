"""判例データモデル"""

from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class CaseDetail(BaseModel):
    """判例詳細データ"""

    case_id: str = Field(..., description="判例ID")
    case_name: str = Field(..., description="事件名")
    court_name: str = Field(..., description="裁判所名")
    decision_date: date = Field(..., description="判決日")
    case_number: Optional[str] = Field(None, description="事件番号")
    case_type: Optional[str] = Field(None, description="事件種別")
    holdings: Optional[str] = Field(None, description="判示事項")
    case_summary: Optional[str] = Field(None, description="裁判要旨")
    main_text: str = Field(..., description="判決全文")
    outcome: Optional[str] = Field(None, description="判決結果")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "case_id": "CASE-2024-001",
                "case_name": "○○事件",
                "court_name": "最高裁判所",
                "decision_date": "2024-01-15",
                "case_number": "令和5年(オ)第1234号",
                "case_type": "民事",
                "holdings": "契約解除の可否について",
                "case_summary": "本件において...",
                "main_text": "主文 1. ...",
                "outcome": "上告棄却",
            }
        }
    )


class CaseReference(BaseModel):
    """判例の引用関係"""

    case_id: str = Field(..., description="引用元の判例ID")
    referenced_law_id: Optional[str] = Field(None, description="引用された法令ID")
    referenced_case_id: Optional[str] = Field(None, description="引用された判例ID")
    reference_type: str = Field(
        default="cites", description="引用タイプ (cites, follows, distinguishes)"
    )
    context: Optional[str] = Field(None, description="引用文脈")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "case_id": "CASE-2024-001",
                "referenced_law_id": "405AC0000000087",
                "reference_type": "cites",
                "context": "民法第309条に基づき...",
            }
        }
    )


class CaseSearchResult(BaseModel):
    """判例検索結果"""

    case_id: str
    case_name: str
    court_name: str
    decision_date: date
    case_type: Optional[str] = None
    relevance_score: Optional[float] = Field(None, ge=0.0, le=1.0)
