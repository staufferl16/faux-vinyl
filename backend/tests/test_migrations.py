from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

BACKEND_DIR = Path(__file__).resolve().parents[1]


def alembic_config():
    config = Config(BACKEND_DIR / "alembic.ini")
    config.set_main_option("script_location", str(BACKEND_DIR / "migrations"))
    return config


def test_upgrade_creates_tables(database_url):
    command.upgrade(alembic_config(), "head")

    tables = inspect(create_engine(database_url)).get_table_names()
    assert {"users", "spotify_tokens"} <= set(tables)


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
    assert not {"users", "spotify_tokens"} & set(tables)
