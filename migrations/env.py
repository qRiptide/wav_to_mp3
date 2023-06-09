import asyncio

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from src.db_conf import settings
from src.models import Base

target_metadata = Base.metadata


def do_run_migrations(connection):
    context.configure(
        compare_type=True,
        dialect_opts={"paramstyle": "named"},
        connection=connection,
        target_metadata=target_metadata,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    connectable = create_async_engine(settings.asyncpg_url, future=True)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


asyncio.run(run_migrations_online())
