import os

from sqlalchemy import create_engine

from app.common.exceptions import EnvNotConfiguredError

if not os.environ.get('DATABASE_URL'):
    raise EnvNotConfiguredError('Please set DATABASE_URL env variable')

engine = create_engine(
    os.environ.get('DATABASE_URL'),  # pyright: ignore[reportArgumentType]
    execution_options={
        'isolation_level': 'REPEATABLE READ',
    },
)
