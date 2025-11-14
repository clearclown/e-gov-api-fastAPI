"""SQLAlchemy database models for case law."""

from datetime import datetime
from typing import Any

from sqlalchemy import (
    TIMESTAMP,
    CheckConstraint,
    Date,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CaseModel(Base):
    """判例テーブル"""

    __tablename__ = "cases"

    case_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    case_number: Mapped[str] = mapped_column(String(100), nullable=False)
    case_name: Mapped[str] = mapped_column(String(500), nullable=False)
    court_type: Mapped[str] = mapped_column(String(50), nullable=False)
    court_name: Mapped[str] = mapped_column(String(100), nullable=False)
    case_type: Mapped[str] = mapped_column(String(50), nullable=False)
    decision_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    main_text: Mapped[str] = mapped_column(Text, nullable=False)
    holdings: Mapped[str | None] = mapped_column(Text, nullable=True)
    case_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    references: Mapped[list["CaseReferenceModel"]] = relationship(
        "CaseReferenceModel",
        back_populates="case",
        cascade="all, delete-orphan",
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "court_type IN ('最高裁判所', '高等裁判所', '地方裁判所', '家庭裁判所', '簡易裁判所')",
            name="check_court_type",
        ),
        CheckConstraint(
            "case_type IN ('民事', '刑事', '行政', '家事')",
            name="check_case_type",
        ),
        Index("idx_cases_decision_date", "decision_date"),
        Index("idx_cases_court_type", "court_type"),
        Index("idx_cases_case_type", "case_type"),
    )


class CaseReferenceModel(Base):
    """判例引用テーブル"""

    __tablename__ = "case_references"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("cases.case_id", ondelete="CASCADE"), nullable=False
    )
    referenced_law_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    referenced_case_id: Mapped[str | None] = mapped_column(
        String(50), ForeignKey("cases.case_id", ondelete="CASCADE"), nullable=True
    )
    reference_type: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, default=datetime.utcnow
    )

    # Relationships
    case: Mapped["CaseModel"] = relationship("CaseModel", back_populates="references")

    # Indexes
    __table_args__ = (Index("idx_case_references_case_id", "case_id"),)
