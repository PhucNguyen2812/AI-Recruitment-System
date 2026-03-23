"""Add ket_qua_xep_hang table

Revision ID: a1b2c3d4e5f6
Revises: 02fb7e3ecdff
Create Date: 2026-03-16 00:30:00.000000+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from app.core.types import GUID

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '02fb7e3ecdff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'ket_qua_xep_hang',
        sa.Column('id', GUID(), nullable=False),
        sa.Column('id_chien_dich', GUID(), nullable=False),
        sa.Column('id_cong_viec', GUID(), nullable=False),
        sa.Column('ho_ten', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('so_dien_thoai', sa.String(20), nullable=True),
        sa.Column('hang', sa.Integer(), nullable=False),
        sa.Column('diem_ahp', sa.Float(), nullable=False),
        sa.Column('nhom', sa.String(20), nullable=False),
        sa.Column('diem_chi_tiet', sa.JSON(), nullable=True),
        sa.Column('ten_cong_viec', sa.String(255), nullable=True),
        sa.Column('ten_chien_dich', sa.String(255), nullable=True),
        sa.Column('ngay_luu', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['id_chien_dich'], ['chien_dich.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_ket_qua_xep_hang_campaign', 'ket_qua_xep_hang', ['id_chien_dich'])
    op.create_index('ix_ket_qua_xep_hang_job', 'ket_qua_xep_hang', ['id_cong_viec'])


def downgrade() -> None:
    op.drop_index('ix_ket_qua_xep_hang_job', table_name='ket_qua_xep_hang')
    op.drop_index('ix_ket_qua_xep_hang_campaign', table_name='ket_qua_xep_hang')
    op.drop_table('ket_qua_xep_hang')
