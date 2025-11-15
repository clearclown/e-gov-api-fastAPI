"""Add fulltext search index

Revision ID: 002
Revises: 001
Create Date: 2025-11-14 01:00:00.000000

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create GIN index for full-text search on cases table
    # Note: This uses PostgreSQL's built-in text search with Japanese support
    op.execute("""
        CREATE INDEX idx_cases_fulltext ON cases USING gin(
            to_tsvector('simple',
                case_name || ' ' ||
                COALESCE(summary, '') || ' ' ||
                main_text
            )
        )
    """)

    # Note: Using 'simple' dictionary instead of 'japanese' for broader compatibility
    # For production with Japanese text search, consider installing pg_bigm or MeCab extensions:
    # - pg_bigm: CREATE EXTENSION pg_bigm;
    # - Then use: CREATE INDEX idx_cases_fulltext ON cases USING gin(case_name gin_bigm_ops);


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_cases_fulltext")
