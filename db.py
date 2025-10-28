import os

from sqlalchemy import create_engine

engine = create_engine(
    os.environ.get('DATABASE_URL'),
    execution_options={
        'isolation_level': 'REPEATABLE READ',
    },
)
