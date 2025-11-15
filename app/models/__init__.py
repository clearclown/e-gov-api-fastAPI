"""Data models for the legal API"""

from app.models.law import LawDetail, LawSearchResult
from app.models.case import CaseDetail

__all__ = ["LawDetail", "LawSearchResult", "CaseDetail"]
