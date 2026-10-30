from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session

from app.core.config import Settings


DATABASE_URL = Settings().DATABASE_URL
is_sqlite = DATABASE_URL.startswith("sqlite")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if is_sqlite else {},
)

if is_sqlite:
    @event.listens_for(engine, "connect")
    def _enable_sqlite_foreign_keys(dbapi_connection, _):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


class Base(DeclarativeBase):
    pass


def get_session():
    with Session(engine) as session:
        yield session


get_db = get_session
