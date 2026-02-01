import os
from typing import Any

from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.common.exceptions import EnvNotConfiguredError


def create_database_engine(
    pool_size: int = 5,
    max_overflow: int = 10,
    pool_pre_ping: bool = True,
    echo: bool = False,
    **kwargs: Any,
) -> AsyncEngine:
    database_url = os.environ.get('DATABASE_URL')  # pyright: ignore[reportArgumentType]

    if not database_url:
        raise EnvNotConfiguredError('Please set DATABASE_URL env variable')

    if database_url.startswith('postgresql://'):
        database_url = database_url.replace('postgresql://', 'postgresql+asyncpg://', 1)

    return create_async_engine(
        database_url,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_pre_ping=pool_pre_ping,
        echo=echo,
        execution_options={
            'isolation_level': 'REPEATABLE READ',
        },
        **kwargs,
    )


def create_sync_engine(
    pool_size: int = 5,
    max_overflow: int = 10,
    pool_pre_ping: bool = True,
    echo: bool = False,
    **kwargs: Any,
) -> Engine:
    """Создаёт синхронный движок для Alembic миграций."""
    database_url = os.environ.get('DATABASE_URL')

    if not database_url:
        raise EnvNotConfiguredError('Please set DATABASE_URL env variable')

    # Убираем asyncpg драйвер для синхронного подключения
    if database_url.startswith('postgresql+asyncpg://'):
        database_url = database_url.replace('postgresql+asyncpg://', 'postgresql://', 1)
    elif not database_url.startswith('postgresql://'):
        database_url = f'postgresql://{database_url}'

    return create_engine(
        database_url,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_pre_ping=pool_pre_ping,
        echo=echo,
        execution_options={
            'isolation_level': 'REPEATABLE READ',
        },
        **kwargs,
    )


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:\
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


sync_engine = create_sync_engine()
engine = create_database_engine()
session_factory = create_session_factory(engine)


async def get_session():
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise


