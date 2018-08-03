from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def engine() -> Engine:
    return create_engine("postgresql://localhost:5433/ke", echo=True)
