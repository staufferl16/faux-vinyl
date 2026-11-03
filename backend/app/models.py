import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Text,
    UniqueConstraint,
    func,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class AuthType(enum.Enum):
    protected = "protected"  # per-user OAuth, e.g. Spotify
    public = "public"  # app-level credentials only
    unsupported = "unsupported"  # listed, but auth isn't implemented yet
    open = "open"  # no auth, e.g. native mp3s


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    active: Mapped[bool] = mapped_column(Boolean, server_default=true())

    music_provider_users: Mapped[list["MusicProviderUser"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )


class MusicProvider(TimestampMixin, Base):
    __tablename__ = "music_providers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)
    url: Mapped[str | None] = mapped_column(String(255))
    auth_type: Mapped[AuthType] = mapped_column(
        Enum(AuthType, name="auth_type", native_enum=False, create_constraint=True)
    )

    music_provider_users: Mapped[list["MusicProviderUser"]] = relationship(
        back_populates="provider"
    )


class MusicProviderUser(TimestampMixin, Base):
    """A user's account with a provider. Native playback needs no row."""

    __tablename__ = "music_provider_users"
    __table_args__ = (
        UniqueConstraint("provider_id", "provider_user_id"),
        UniqueConstraint("user_id", "provider_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    provider_id: Mapped[int] = mapped_column(
        ForeignKey("music_providers.id", ondelete="RESTRICT")
    )
    provider_user_id: Mapped[str] = mapped_column(String(255))
    username: Mapped[str | None] = mapped_column(String(255))

    # Only used by providers with AuthType.protected.
    encrypted_refresh_token: Mapped[bytes | None] = mapped_column(LargeBinary)
    access_token: Mapped[str | None] = mapped_column(Text)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    scopes: Mapped[str | None] = mapped_column(Text)

    user: Mapped[User] = relationship(back_populates="music_provider_users")
    provider: Mapped[MusicProvider] = relationship(
        back_populates="music_provider_users"
    )
