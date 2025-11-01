import os

from fastapi import Depends
from pydantic import Annotated
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

engine = create_engine(
    os.environ.get('DATABASE_URL'),
    execution_options={
        'isolation_level': 'REPEATABLE READ',
    },
)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
