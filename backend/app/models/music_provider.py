import enum
from typing import TYPE_CHECKING

from sqlalchemy import Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base
from .mixins import TimestampMixin

if TYPE_CHECKING:
    from .music_provider_user import MusicProviderUser


class ProviderName(enum.Enum):
    spotify = "spotify"
    native = "native"  # Faux Vinyl's own mp3s


class AuthType(enum.Enum):
    protected = "protected"  # per-user OAuth, e.g. Spotify
    public = "public"  # app-level credentials only
    unsupported = "unsupported"  # listed, but auth isn't implemented yet
    open = "open"  # no auth, e.g. native mp3s


class MusicProvider(TimestampMixin, Base):
    __tablename__ = "music_providers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[ProviderName] = mapped_column(
        Enum(
            ProviderName,
            name="provider_name",
            native_enum=False,
            create_constraint=True,
        ),
        unique=True,
    )
    display_name: Mapped[str] = mapped_column(String(64))
    url: Mapped[str | None] = mapped_column(String(255))
    auth_type: Mapped[AuthType] = mapped_column(
        Enum(AuthType, name="auth_type", native_enum=False, create_constraint=True)
    )

    music_provider_users: Mapped[list["MusicProviderUser"]] = relationship(
        back_populates="provider"
    )
