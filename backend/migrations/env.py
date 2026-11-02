from alembic import context

from app import config as app_config
from app import models  # noqa: F401  (registers tables on Base.metadata)
from app.db import Base, make_engine

target_metadata = Base.metadata


def run_migrations_offline():
    context.configure(
        url=app_config.database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    engine = make_engine(app_config.database_url())
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
