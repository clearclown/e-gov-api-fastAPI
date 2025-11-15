"""Initial case tables

Revision ID: 001
Revises:
Create Date: 2025-11-14 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create cases table
    op.create_table(
        'cases',
        sa.Column('case_id', sa.String(length=50), nullable=False),
        sa.Column('case_number', sa.String(length=100), nullable=False),
        sa.Column('case_name', sa.String(length=500), nullable=False),
        sa.Column('court_type', sa.String(length=50), nullable=False),
        sa.Column('court_name', sa.String(length=100), nullable=False),
        sa.Column('case_type', sa.String(length=50), nullable=False),
        sa.Column('decision_date', sa.Date(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('main_text', sa.Text(), nullable=False),
        sa.Column('holdings', sa.Text(), nullable=True),
        sa.Column('case_summary', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint(
            "court_type IN ('最高裁判所', '高等裁判所', '地方裁判所', '家庭裁判所', '簡易裁判所')",
            name='check_court_type'
        ),
        sa.CheckConstraint(
            "case_type IN ('民事', '刑事', '行政', '家事')",
            name='check_case_type'
        ),
        sa.PrimaryKeyConstraint('case_id')
    )

    # Create indexes on cases table
    op.create_index('idx_cases_decision_date', 'cases', ['decision_date'], unique=False)
    op.create_index('idx_cases_court_type', 'cases', ['court_type'], unique=False)
    op.create_index('idx_cases_case_type', 'cases', ['case_type'], unique=False)

    # Create case_references table
    op.create_table(
        'case_references',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('case_id', sa.String(length=50), nullable=False),
        sa.Column('referenced_law_id', sa.String(length=50), nullable=True),
        sa.Column('referenced_case_id', sa.String(length=50), nullable=True),
        sa.Column('reference_type', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['case_id'], ['cases.case_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['referenced_case_id'], ['cases.case_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create index on case_references table
    op.create_index('idx_case_references_case_id', 'case_references', ['case_id'], unique=False)


def downgrade() -> None:
    # Drop indexes and tables
    op.drop_index('idx_case_references_case_id', table_name='case_references')
    op.drop_table('case_references')
    op.drop_index('idx_cases_case_type', table_name='cases')
    op.drop_index('idx_cases_court_type', table_name='cases')
    op.drop_index('idx_cases_decision_date', table_name='cases')
    op.drop_table('cases')
