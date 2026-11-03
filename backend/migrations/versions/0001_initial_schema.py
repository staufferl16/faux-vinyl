"""users, music_providers and music_provider_users

Revision ID: 0001
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

AUTH_TYPES = ("protected", "public", "unsupported", "open")


def timestamps():
    return [
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    ]


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("active", sa.Boolean(), server_default=sa.true(), nullable=False),
        *timestamps(),
    )
    music_providers = op.create_table(
        "music_providers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("url", sa.String(length=255), nullable=True),
        sa.Column(
            "auth_type",
            sa.Enum(
                *AUTH_TYPES,
                name="auth_type",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        *timestamps(),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "music_provider_users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "provider_id",
            sa.Integer(),
            sa.ForeignKey("music_providers.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("provider_user_id", sa.String(length=255), nullable=False),
        sa.Column("username", sa.String(length=255), nullable=True),
        sa.Column("encrypted_refresh_token", sa.LargeBinary(), nullable=True),
        sa.Column("access_token", sa.Text(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("scopes", sa.Text(), nullable=True),
        *timestamps(),
        sa.UniqueConstraint("provider_id", "provider_user_id"),
        sa.UniqueConstraint("user_id", "provider_id"),
    )

    op.bulk_insert(
        music_providers,
        [
            {
                "name": "spotify",
                "url": "https://api.spotify.com/v1",
                "auth_type": "protected",
            },
            {"name": "native", "url": None, "auth_type": "open"},
        ],
    )


def downgrade():
    op.drop_table("music_provider_users")
    op.drop_table("music_providers")
    op.drop_table("users")
