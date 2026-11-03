from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base
from .mixins import TimestampMixin

if TYPE_CHECKING:
    from .music_provider import MusicProvider
    from .user import User


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

    user: Mapped["User"] = relationship(back_populates="music_provider_users")
    provider: Mapped["MusicProvider"] = relationship(
        back_populates="music_provider_users"
    )
