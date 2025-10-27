from sqlalchemy import create_engine

engine = create_engine(
    "postgresql+pg8000://scott:tiger@localhost/test",
    execution_options={
        "isolation_level": "REPEATABLE READ"
    }
)