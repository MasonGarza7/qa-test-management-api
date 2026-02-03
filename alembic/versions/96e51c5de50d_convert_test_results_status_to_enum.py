"""convert test_results.status to enum

Revision ID: 96e51c5de50d
Revises: c267093f0aa9
Create Date: 2026-02-01 23:32:33.789810

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '96e51c5de50d'
down_revision: Union[str, Sequence[str], None] = 'c267093f0aa9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1) Create the enum type (if it doesn't already exist)
    test_status = sa.Enum("pass", "fail", "blocked", "skipped", name="test_status")
    test_status.create(op.get_bind(), checkfirst=True)

    # 2) Alter the column to use the enum type
    op.alter_column(
        "test_results",
        "status",
        existing_type=sa.String(length=20),
        type_=test_status,
        postgresql_using="status::test_status",
        existing_nullable=False,
    )


def downgrade() -> None:
    test_status = sa.Enum("pass", "fail", "blocked", "skipped", name="test_status")

    op.alter_column(
        "test_results",
        "status",
        existing_type=test_status,
        type_=sa.String(length=20),
        existing_nullable=False,
    )

    test_status.drop(op.get_bind(), checkfirst=True)
    