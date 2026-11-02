"""users and spotify_tokens

Revision ID: 0001
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("spotify_id", sa.String(length=255), primary_key=True),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_table(
        "spotify_tokens",
        sa.Column(
            "user_id",
            sa.String(length=255),
            sa.ForeignKey("users.spotify_id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("encrypted_refresh_token", sa.LargeBinary(), nullable=False),
        sa.Column("access_token", sa.Text(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade():
    op.drop_table("spotify_tokens")
    op.drop_table("users")
