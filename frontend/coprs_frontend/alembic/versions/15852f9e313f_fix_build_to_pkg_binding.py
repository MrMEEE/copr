"""intermediate revision to rebind builds to a unique package name in a given project

Revision ID: 15852f9e313f
Revises: 3341bf554454
Create Date: 2014-04-04 11:25:36.216132

"""

# revision identifiers, used by Alembic.
revision = '15852f9e313f'
down_revision = '3341bf554454'

from alembic import op
import sqlalchemy as sa


def upgrade():
    bind = op.get_bind()
    connection = bind.connect()
    connection.execute("""
        UPDATE build SET package_id=188513 WHERE package_id=188514;
    """) # nathans / pcp.io / parfaits
    connection.execute("""
        UPDATE build SET package_id=188411 WHERE package_id=188412;
    """) # abutcher / ansible / python-passlib
    connection.execute("""
        UPDATE build SET package_id=186389 WHERE package_id=186390;
    """) # decathorpe / elementary-nightly / elementary-dpms-helper
    connection.execute("""
        UPDATE build SET package_id=188701 WHERE package_id=188702;
    """) # @abrt / retrace-server-devel / retrace-server
    connection.close()

def downgrade():
    # this migration is only one-way
    pass
