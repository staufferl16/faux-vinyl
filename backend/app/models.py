from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, LargeBinary, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class User(Base):
    __tablename__ = "users"

    spotify_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    display_name: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class SpotifyToken(Base):
    __tablename__ = "spotify_tokens"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.spotify_id", ondelete="CASCADE"), primary_key=True
    )
    encrypted_refresh_token: Mapped[bytes] = mapped_column(LargeBinary)
    access_token: Mapped[str | None] = mapped_column(Text)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
