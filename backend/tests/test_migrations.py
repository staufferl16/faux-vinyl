from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import make_engine
from app.models import AuthType, MusicProvider, MusicProviderUser, User

BACKEND_DIR = Path(__file__).resolve().parents[1]
TABLES = {"users", "music_providers", "music_provider_users"}


def alembic_config():
    config = Config(BACKEND_DIR / "alembic.ini")
    config.set_main_option("script_location", str(BACKEND_DIR / "migrations"))
    return config


@pytest.fixture
def session(database_url):
    command.upgrade(alembic_config(), "head")
    with Session(make_engine(database_url)) as session:
        yield session


def add_spotify_account(session, user, provider_user_id="spotify-user"):
    spotify = session.scalars(
        select(MusicProvider).where(MusicProvider.name == "spotify")
    ).one()
    account = MusicProviderUser(
        user=user, provider=spotify, provider_user_id=provider_user_id
    )
    session.add(account)
    session.flush()
    return account


def test_upgrade_creates_tables(database_url):
    command.upgrade(alembic_config(), "head")

    tables = inspect(create_engine(database_url)).get_table_names()
    assert TABLES <= set(tables)


def test_models_match_migrations(database_url):
    config = alembic_config()
    command.upgrade(config, "head")

    # Raises if the models have changes with no migration.
    command.check(config)


def test_downgrade_removes_tables(database_url):
    config = alembic_config()
    command.upgrade(config, "head")
    command.downgrade(config, "base")

    tables = inspect(create_engine(database_url)).get_table_names()
    assert not TABLES & set(tables)


def test_upgrade_seeds_providers(session):
    providers = {p.name: p for p in session.scalars(select(MusicProvider))}

    assert providers["spotify"].auth_type is AuthType.protected
    assert providers["spotify"].url == "https://api.spotify.com/v1"
    assert providers["native"].auth_type is AuthType.open
    assert providers["native"].url is None


def test_new_user_defaults(session):
    user = User()
    session.add(user)
    session.flush()
    session.refresh(user)

    assert user.active is True
    assert user.created_at is not None
    assert user.updated_at is not None


def test_provider_account_belongs_to_one_user(session):
    add_spotify_account(session, User())

    with pytest.raises(IntegrityError):
        add_spotify_account(session, User())


def test_deleting_user_deletes_accounts(session):
    user = User()
    add_spotify_account(session, user)
    session.commit()

    session.execute(text("DELETE FROM users"))
    session.commit()

    assert session.scalars(select(MusicProviderUser)).all() == []


def test_invalid_auth_type_is_rejected(session):
    with pytest.raises(IntegrityError):
        session.execute(
            text(
                "INSERT INTO music_providers (name, auth_type) "
                "VALUES ('bogus', 'secret')"
            )
        )
