"""Case law data models."""

from datetime import date
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class CourtType(str, Enum):
    """裁判所種別"""

    SUPREME = "最高裁判所"
    HIGH = "高等裁判所"
    DISTRICT = "地方裁判所"
    FAMILY = "家庭裁判所"
    SUMMARY = "簡易裁判所"


class CaseType(str, Enum):
    """事件種別"""

    CIVIL = "民事"
    CRIMINAL = "刑事"
    ADMINISTRATIVE = "行政"
    FAMILY = "家事"


class CaseSearchResult(BaseModel):
    """判例検索結果"""

    case_id: str = Field(..., description="判例ID")
    case_number: str = Field(..., description="事件番号（例: 令和2年(オ)第123号）")
    case_name: str = Field(..., description="事件名")
    court_type: CourtType = Field(..., description="裁判所種別")
    court_name: str = Field(..., description="裁判所名（例: 東京高等裁判所）")
    case_type: CaseType = Field(..., description="事件種別")
    decision_date: date = Field(..., description="判決日")
    summary: Optional[str] = Field(None, description="要旨")


class CaseDetail(BaseModel):
    """判例詳細"""

    case_id: str = Field(..., description="判例ID")
    case_number: str = Field(..., description="事件番号")
    case_name: str = Field(..., description="事件名")
    court_type: CourtType = Field(..., description="裁判所種別")
    court_name: str = Field(..., description="裁判所名")
    case_type: CaseType = Field(..., description="事件種別")
    decision_date: date = Field(..., description="判決日")
    summary: Optional[str] = Field(None, description="要旨")
    main_text: str = Field(..., description="判決全文")
    holdings: Optional[str] = Field(None, description="判示事項")
    case_summary: Optional[str] = Field(None, description="裁判要旨")
    references: list[str] = Field(default_factory=list, description="参照法令")
    related_cases: list[str] = Field(default_factory=list, description="関連判例")
    metadata: dict[str, Any] = Field(default_factory=dict, description="メタデータ")


class CaseReference(BaseModel):
    """判例引用情報"""

    case_id: str = Field(..., description="判例ID")
    referenced_law_id: Optional[str] = Field(None, description="引用法令ID")
    referenced_case_id: Optional[str] = Field(None, description="引用判例ID")
    reference_type: str = Field(..., description="引用種別")
