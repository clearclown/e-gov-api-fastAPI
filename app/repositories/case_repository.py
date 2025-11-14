"""Repository for case law data access."""

from datetime import date
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import CaseModel, CaseReferenceModel
from app.models.case import CaseDetail, CaseSearchResult, CaseType, CourtType


class CaseRepository:
    """判例データベースアクセス"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_case(self, case: CaseDetail) -> str:
        """判例を保存"""
        # Check if case already exists
        existing = await self.session.get(CaseModel, case.case_id)

        if existing:
            # Update existing case
            existing.case_number = case.case_number
            existing.case_name = case.case_name
            existing.court_type = case.court_type.value
            existing.court_name = case.court_name
            existing.case_type = case.case_type.value
            existing.decision_date = case.decision_date
            existing.summary = case.summary
            existing.main_text = case.main_text
            existing.holdings = case.holdings
            existing.case_summary = case.case_summary
            existing.metadata = case.metadata
        else:
            # Create new case
            case_model = CaseModel(
                case_id=case.case_id,
                case_number=case.case_number,
                case_name=case.case_name,
                court_type=case.court_type.value,
                court_name=case.court_name,
                case_type=case.case_type.value,
                decision_date=case.decision_date,
                summary=case.summary,
                main_text=case.main_text,
                holdings=case.holdings,
                case_summary=case.case_summary,
                metadata=case.metadata,
            )
            self.session.add(case_model)

        # Handle references
        if case.references or case.related_cases:
            # Delete existing references
            await self.session.execute(
                select(CaseReferenceModel).where(CaseReferenceModel.case_id == case.case_id)
            )

            # Add law references
            for law_id in case.references:
                ref = CaseReferenceModel(
                    case_id=case.case_id,
                    referenced_law_id=law_id,
                    reference_type="law",
                )
                self.session.add(ref)

            # Add case references
            for related_case_id in case.related_cases:
                ref = CaseReferenceModel(
                    case_id=case.case_id,
                    referenced_case_id=related_case_id,
                    reference_type="case",
                )
                self.session.add(ref)

        await self.session.flush()
        return case.case_id

    async def get_case_by_id(self, case_id: str) -> CaseDetail | None:
        """判例IDで取得"""
        case_model = await self.session.get(CaseModel, case_id)

        if not case_model:
            return None

        # Get references
        law_refs_result = await self.session.execute(
            select(CaseReferenceModel.referenced_law_id).where(
                CaseReferenceModel.case_id == case_id,
                CaseReferenceModel.referenced_law_id.isnot(None),
            )
        )
        law_refs = [row[0] for row in law_refs_result.all() if row[0]]

        case_refs_result = await self.session.execute(
            select(CaseReferenceModel.referenced_case_id).where(
                CaseReferenceModel.case_id == case_id,
                CaseReferenceModel.referenced_case_id.isnot(None),
            )
        )
        case_refs = [row[0] for row in case_refs_result.all() if row[0]]

        return CaseDetail(
            case_id=case_model.case_id,
            case_number=case_model.case_number,
            case_name=case_model.case_name,
            court_type=CourtType(case_model.court_type),
            court_name=case_model.court_name,
            case_type=CaseType(case_model.case_type),
            decision_date=case_model.decision_date,
            summary=case_model.summary,
            main_text=case_model.main_text,
            holdings=case_model.holdings,
            case_summary=case_model.case_summary,
            references=law_refs,
            related_cases=case_refs,
            metadata=case_model.metadata or {},
        )

    async def search_cases(
        self,
        query: str | None = None,
        court_type: str | None = None,
        case_type: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[CaseSearchResult], int]:
        """判例検索（全文検索対応）"""
        # Build base query
        stmt = select(CaseModel)

        # Apply filters
        if query:
            # Simple text search (can be enhanced with PostgreSQL full-text search)
            search_filter = (
                CaseModel.case_name.ilike(f"%{query}%")
                | CaseModel.summary.ilike(f"%{query}%")
                | CaseModel.main_text.ilike(f"%{query}%")
            )
            stmt = stmt.where(search_filter)

        if court_type:
            stmt = stmt.where(CaseModel.court_type == court_type)

        if case_type:
            stmt = stmt.where(CaseModel.case_type == case_type)

        if date_from:
            stmt = stmt.where(CaseModel.decision_date >= date_from)

        if date_to:
            stmt = stmt.where(CaseModel.decision_date <= date_to)

        # Get total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar() or 0

        # Apply pagination and ordering
        stmt = stmt.order_by(CaseModel.decision_date.desc()).limit(limit).offset(offset)

        # Execute query
        result = await self.session.execute(stmt)
        cases = result.scalars().all()

        # Convert to search results
        search_results = [
            CaseSearchResult(
                case_id=case.case_id,
                case_number=case.case_number,
                case_name=case.case_name,
                court_type=CourtType(case.court_type),
                court_name=case.court_name,
                case_type=CaseType(case.case_type),
                decision_date=case.decision_date,
                summary=case.summary,
            )
            for case in cases
        ]

        return search_results, total

    async def get_cases_by_law(
        self, law_id: str, limit: int = 50, offset: int = 0
    ) -> tuple[list[CaseSearchResult], int]:
        """特定の法令を引用している判例を取得"""
        # Build query with join
        stmt = (
            select(CaseModel)
            .join(CaseReferenceModel, CaseModel.case_id == CaseReferenceModel.case_id)
            .where(CaseReferenceModel.referenced_law_id == law_id)
        )

        # Get total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar() or 0

        # Apply pagination and ordering
        stmt = stmt.order_by(CaseModel.decision_date.desc()).limit(limit).offset(offset)

        # Execute query
        result = await self.session.execute(stmt)
        cases = result.scalars().all()

        # Convert to search results
        search_results = [
            CaseSearchResult(
                case_id=case.case_id,
                case_number=case.case_number,
                case_name=case.case_name,
                court_type=CourtType(case.court_type),
                court_name=case.court_name,
                case_type=CaseType(case.case_type),
                decision_date=case.decision_date,
                summary=case.summary,
            )
            for case in cases
        ]

        return search_results, total
