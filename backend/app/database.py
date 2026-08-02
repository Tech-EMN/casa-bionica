"""Casa Biônica — Database engine + session (sync SQLAlchemy + psycopg2).

Usa psycopg2 (sync) em vez de asyncpg porque o Supabase usa SNI-based routing
que o asyncpg não suporta nativamente.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session

from .config import settings

engine = create_engine(
    settings.database_url,
    echo=(settings.log_level == "DEBUG"),
    pool_size=5,
    max_overflow=10,
)

SessionLocal = None


def get_db() -> Session:
    """Dependency: retorna uma session do SQLAlchemy (sync)."""
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()


class Base(DeclarativeBase):
    pass
