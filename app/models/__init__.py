"""Data models for the legal API"""

from app.models.law import LawDetail, LawSummary
from app.models.case import CaseDetail, CaseSummary

__all__ = ["LawDetail", "LawSummary", "CaseDetail", "CaseSummary"]
