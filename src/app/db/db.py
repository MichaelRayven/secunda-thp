import os
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

engine = create_engine(
    os.environ.get('DATABASE_URL'), # type: ignore
    execution_options={
        'isolation_level': 'REPEATABLE READ',
    },
)
