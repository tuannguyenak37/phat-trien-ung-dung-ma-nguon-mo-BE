"""Add status column to users

Revision ID: ed4e1affb92e
Revises: f2e3df019eaf
Create Date: 2025-12-02 13:50:08.723155

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ed4e1affb92e'
down_revision: Union[str, Sequence[str], None] = 'f2e3df019eaf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Định nghĩa và tạo Enum Type trong Postgres trước
    # Lưu ý: Cần thêm 'PENDING' cho khớp với Model Python
    user_status_enum = sa.Enum('ACTIVE', 'BANNED', name='userstatus')
    user_status_enum.create(op.get_bind())

    # 2. Thêm cột status
    # server_default='ACTIVE' là bắt buộc để điền dữ liệu cho các user cũ
    op.add_column('users', sa.Column('status', user_status_enum, nullable=False, server_default='ACTIVE'))

    # 3. Các lệnh thay đổi khác (do Alembic tự sinh ra)
    op.drop_column('users', 'url_bg')
    
    op.alter_column('votes', 'user_id',
               existing_type=sa.VARCHAR(length=50),
               nullable=False)
               
    op.create_unique_constraint('uq_vote_user_comment', 'votes', ['user_id', 'comment_id'])
    op.create_unique_constraint('uq_vote_user_thread', 'votes', ['user_id', 'thread_id'])


def downgrade() -> None:
    """Downgrade schema."""
    # 1. Xóa các ràng buộc và cột (ngược lại với upgrade)
    op.drop_constraint('uq_vote_user_thread', 'votes', type_='unique')
    op.drop_constraint('uq_vote_user_comment', 'votes', type_='unique')
    
    op.alter_column('votes', 'user_id',
               existing_type=sa.VARCHAR(length=50),
               nullable=True)
               
    op.add_column('users', sa.Column('url_bg', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    
    # 2. Xóa cột status
    op.drop_column('users', 'status')

    # 3. Xóa Type Enum cuối cùng
    sa.Enum(name='userstatus').drop(op.get_bind())