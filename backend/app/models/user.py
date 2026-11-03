from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base
from .mixins import TimestampMixin

if TYPE_CHECKING:
    from .music_provider_user import MusicProviderUser


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    active: Mapped[bool] = mapped_column(Boolean, server_default=true())

    music_provider_users: Mapped[list["MusicProviderUser"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )
